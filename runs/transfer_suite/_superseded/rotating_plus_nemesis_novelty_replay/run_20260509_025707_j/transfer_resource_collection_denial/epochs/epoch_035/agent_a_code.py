def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list if p is not None and len(p) >= 2}
    resources = observation.get("resources", []) or []

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    res = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if ok(rx, ry):
            res.append((rx, ry))
    if not res:
        return [0, 0]

    best = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        local_best = None
        for (rx, ry) in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; then closer to the target.
            # Also prefer moves that push opponent further away (via -opp_dist).
            val = (sd - od, sd, -od, rx, ry)
            if local_best is None or val < local_best:
                local_best = val
        if local_best is None:
            continue
        # Tie-break deterministically by move.
        top = (local_best[0], local_best[1], local_best[2], local_best[3], local_best[4], dx, dy)
        if best is None or top < best:
            best = top
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]