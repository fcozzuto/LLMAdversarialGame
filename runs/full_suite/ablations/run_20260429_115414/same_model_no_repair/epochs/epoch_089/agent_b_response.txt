def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Score: prefer making ourselves closer than opponent to some resource,
        # then prefer reducing our own distance (tie-break deterministic by resource order).
        val = -10**18
        for i, (rx, ry) in enumerate(res):
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                score = 10**7 - i  # strongest: collect immediately
            else:
                score = (opd - myd) * 200 - myd - i * 0.01
            if score > val:
                val = score

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # deterministic tie-break: prefer smaller dx^2+dy^2, then lexicographic
            curd = best_move[0]*best_move[0] + best_move[1]*best_move[1]
            nd = dx*dx + dy*dy
            if nd < curd or (nd == curd and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]