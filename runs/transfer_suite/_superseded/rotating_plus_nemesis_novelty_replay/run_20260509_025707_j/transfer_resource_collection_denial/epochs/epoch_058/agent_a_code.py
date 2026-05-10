def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None  # (score, my_sd, opp_sd, dx, dy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        best_move = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            my_sd = man(nx, ny, rx, ry)
            opp_sd = man(ox, oy, rx, ry)
            can_win = opp_sd - my_sd  # positive means we get there first (or equal)
            # Encourage early wins, then closeness and centralization to reduce dithering.
            central = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))  # closer to center => higher
            row_col_risk = 0
            if rx == nx:  # could be lined up with opponent sweep
                row_col_risk = -0.25
            if ry == ny:
                row_col_risk = -0.25
            score = can_win * 2.0 + central * 0.03 + (-my_sd) * 0.02 + row_col_risk
            cand = (score, my_sd, opp_sd, dx, dy)
            if best_move is None or cand > best_move:
                best_move = cand
        if best_move is not None:
            if best is None or best_move > best:
                best = best_move

    if best is None:
        return [0, 0]
    return [best[3], best[4]]