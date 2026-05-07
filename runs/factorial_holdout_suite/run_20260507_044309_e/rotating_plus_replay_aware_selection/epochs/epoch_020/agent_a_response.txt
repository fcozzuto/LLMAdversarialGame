def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    cx, cy = w // 2, h // 2
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_key = None
    best_fallback = None

    # If no resources, move toward center.
    if not resources:
        tx = 0 if sx == cx else (1 if sx < cx else -1)
        ty = 0 if sy == cy else (1 if sy < cy else -1)
        return [tx, ty]

    # Precompute opponent distances for tie-breaking against resources.
    opp_d = {}
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        opp_d[(rx, ry)] = cheb(ox, oy, rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        my_best = None  # (lead, -ds, center_bias, rx, ry)
        for rx, ry in resources:
            if (rx, ry) not in opp_d:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = opp_d[(rx, ry)]
            lead = do - ds  # >0 means we are closer (earlier under Cheb)
            center_bias = cheb(rx, ry, cx, cy)
            key = (lead, -ds, -center_bias, -rx, -ry)
            if my_best is None or key > my_best:
                my_best = key

        if my_best is None:
            continue

        # Move score: prioritize beating opponent (lead), then fastest capture, then center.
        score_key = (my_best[0], my_best[1], my_best[2], my_best[3], my_best[4], -cheb(nx, ny, cx, cy))
        if best_key is None or score_key > best_key:
            best_key = score_key
            best_move = (dx, dy)
        elif best_key is None:
            best_move = (dx, dy)

        # Fallback if lead is negative everywhere: take closest resource to improve over denial.
        if my_best[0] < 0:
            cand = (-my_best[0], -my_best[1], my_best[2], dx, dy)
            if best_fallback is None or cand < best_fallback:
                best_fallback = cand

    if best_key is None and best_fallback is not None:
        return [best_fallback[3], best_fallback[4]]

    return [best_move[0], best_move[1]]