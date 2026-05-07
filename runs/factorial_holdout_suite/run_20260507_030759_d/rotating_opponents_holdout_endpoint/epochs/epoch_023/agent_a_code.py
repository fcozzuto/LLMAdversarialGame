def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            score = (-10**9, 10**9, 10**9)
        else:
            # Choose the resource we are best positioned to "claim first" from (nx, ny)
            local_best = None
            for r in resources:
                r0, r1 = r[0], r[1]
                sd = dist((nx, ny), (r0, r1))
                od = dist((ox, oy), (r0, r1))
                val = (od - sd, -sd)  # maximize advantage; then prefer closer
                if local_best is None or val > local_best:
                    local_best = val
            # Prefer actions that increase advantage; small tiebreakers to keep determinism
            score = (local_best[0], local_best[1], -(abs(nx - ox) + abs(ny - oy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]