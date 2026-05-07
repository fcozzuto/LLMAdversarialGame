def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid_moves.append((dx, dy))

    if not valid_moves:
        return [0, 0]

    if not resources:
        # Deterministic drift to far corner from opponent
        tx = 0 if sx > w - 1 - sx else w - 1
        ty = 0 if sy > h - 1 - sy else h - 1
        best = None
        bestd = None
        for dx, dy in valid_moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            if bestd is None or d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target resource where we are currently relatively closer than opponent.
    def score_res(rx, ry):
        ds = abs(sx - rx) + abs(sy - ry)
        do = abs(ox - rx) + abs(oy - ry)
        # Prefer resources we can reach earlier (ds - do small/negative),
        # then closer overall.
        return (ds - do, ds, ry, rx)

    resources_sorted = sorted(resources, key=lambda p: score_res(p[0], p[1]))
    target = resources_sorted[0]

    rx, ry = target
    best_move = (0, 0)
    best_val = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        ds_next = abs(nx - rx) + abs(ny - ry)

        # If we move onto a resource, strongly prefer it.
        on_resource = (nx, ny) in resources_set if False else False

        # Approximate "contestation": after move, how much closer are we vs opponent to that resource?
        do = abs(ox - rx) + abs(oy - ry)
        contest = (ds_next - do, ds_next)

        # Deterministic tie-break: prefer moves that reduce both coordinates when possible, else lexicographic.
        val = (contest[0], contest[1], -(dx == 0 and dy == 0), abs(dx) + abs(dy), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]