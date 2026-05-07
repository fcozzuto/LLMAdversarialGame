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

    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2
    best = None
    best_score = -10**9

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        step_x = 0 if rx == ox else (1 if rx > ox else -1)
        step_y = 0 if ry == oy else (1 if ry > oy else -1)
        pred_ox, pred_oy = ox + step_x, oy + step_y
        opp_block_bonus = 4.0 if (pred_ox < 0 or pred_ox >= w or pred_oy < 0 or pred_oy >= h or (pred_ox, pred_oy) in obstacles) else 0.0
        self_central = -(abs(sx - cx) + abs(sy - cy))
        res_central = -(abs(rx - cx) + abs(ry - cy))
        score = (do - ds) + opp_block_bonus + 0.15 * (res_central - self_central)
        if score > best_score:
            best_score = score
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # If diagonal step blocked, fall back deterministically to axis step(s) or stay.
    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    for ddx, ddy in candidates:
        nx, ny = sx + ddx, sy + ddy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(ddx), int(ddy)]
    return [0, 0]