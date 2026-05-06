def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0: dx = -dx
        dy = by - ay
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_valid(x, y):
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            return x, y
        return sx, sy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_same_row = (ox == sy)
    opp_same_col = (oy == sx)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = clamp_valid(sx + dx, sy + dy)

        # Heuristic: pick a resource that maximizes win margin vs opponent, but penalize
        # moves that stay aligned with opponent (helps against row/line sweep behavior).
        local_best = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            margin = opd - myd  # positive means we are closer (good)
            quick = -(myd)    # smaller myd is better
            align_pen = 0
            if ox == nx: align_pen += 1  # aligned in column with opponent
            if oy == ny: align_pen += 1  # aligned in row with opponent
            if opp_same_row and ry == ny: align_pen += 1
            if opp_same_col and rx == nx: align_pen += 1

            val = (margin, quick, -align_pen, -abs(rx - nx) - abs(ry - ny), -((rx + ry) % 2))
            if local_best is None or val > local_best:
                local_best = val

        if best_score is None or local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]