def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        our_d = 10**9
        opp_d = 10**9
        best_margin = -10**9
        best_res_d = None
        for rx, ry in resources:
            d_our = md(nx, ny, rx, ry)
            if d_our < our_d:
                our_d = d_our
                best_res_d = d_our
            d_opp = md(ox, oy, rx, ry)
            if d_opp < opp_d:
                opp_d = d_opp
            margin = d_opp - d_our
            if margin > best_margin:
                best_margin = margin

        # Score: prioritize arriving earlier (margin), then reduce own distance, then slow opponent.
        score = (best_margin * 10) - (our_d * 2) + (opp_d * 0.3)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prefer lower our_d, then higher margin, then closer to opponent
            if our_d < md(sx + best_move[0], sy + best_move[1], resources[0][0], resources[0][1]):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]