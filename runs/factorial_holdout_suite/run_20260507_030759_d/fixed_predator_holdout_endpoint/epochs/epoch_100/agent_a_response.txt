def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        # Chebyshev distance suits diagonal moves
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    # Consider at most some resources for brevity; deterministic ordering by position
    resources = sorted(resources)
    resources = resources[:min(20, len(resources))]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        local_best = None
        for rx, ry in resources:
            r = (rx, ry)
            sd = dist((nx, ny), r)
            od = dist((ox, oy), r)
            # prioritize arriving earlier; tie-break to closer self
            key = (od - sd, -sd)
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue

        # secondary tie-break: move that reduces distance to the best resource from current
        # pick closest among resources by self distance only (deterministic)
        target = min(resources, key=lambda r: (dist((sx, sy), r), r))
        tie_key = -dist((nx, ny), target)
        move_key = (local_best[0], local_best[1], tie_key, -abs(dx) - abs(dy), dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]