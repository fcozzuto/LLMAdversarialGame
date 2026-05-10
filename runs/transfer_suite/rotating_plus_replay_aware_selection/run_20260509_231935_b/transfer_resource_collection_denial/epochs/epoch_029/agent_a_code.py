def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1, h - 1
        if sx < w // 2: tx = 0
        if sx > w // 2: tx = w - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Evaluate each move: maximize advantage in "who reaches resources first".
    best_score = -10**18
    best_move = [0, 0]
    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        cnt_closer = 0
        best_gap = -10**9
        min_our = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            our_d = dist8(nx, ny, rx, ry)
            opp_d = dist8(ox, oy, rx, ry)
            if our_d < opp_d:
                cnt_closer += 1
                gap = opp_d - our_d
                if gap > best_gap: best_gap = gap
            if our_d < min_our: min_our = our_d
            if opp_d < min_opp: min_opp = opp_d

        # If we can beat any resource, prioritize beating many and then biggest gap.
        # Otherwise, reduce opponent lead towards the resource where we lag least.
        if cnt_closer > 0:
            score = cnt_closer * 1000 + best_gap * 50 - min_our
        else:
            # compute "closest lag": smallest (our_d - opp_d)
            lag = 10**9
            for rx, ry in resources:
                our_d = dist8(nx, ny, rx, ry)
                opp_d = dist8(ox, oy, rx, ry)
                diff = our_d - opp_d
                if diff < lag: lag = diff
            score = -lag * 1000 - min_our + min_opp  # less positive lag is better

        if score > best_score:
            best_score = score
            best_move = [mx, my]

    return [best_move[0], best_move[1]]