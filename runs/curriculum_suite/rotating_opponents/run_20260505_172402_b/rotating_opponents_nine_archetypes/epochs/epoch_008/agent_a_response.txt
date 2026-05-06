def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]
    obs = {(p[0], p[1]) for p in obstacles}

    def dist(x1, y1, x2, y2):
        return abs(x2 - x1) + abs(y2 - y1)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    # Compute for a position how good the best contested resource is for us
    def position_value(px, py):
        myd_best = 10**9
        oppd_best = 0
        for rx, ry in resources:
            myd = dist(px, py, rx, ry)
            opd = dist(ox, oy, rx, ry)
            adv = opd - myd  # positive => we're closer
            # If we're clearly winning that resource, strongly prefer it
            if adv > 0:
                score = 2.2 * adv + (18 - myd) * 0.05
            else:
                # If we're losing, only take it if we can swing quickly
                score = 0.3 * adv - 0.02 * myd
            # Mild deterministic preference toward mid-grid resources to reduce diagonal probing
            mid_bias = -0.001 * ((rx - (w - 1) / 2) ** 2 + (ry - (h - 1) / 2) ** 2)
            score += mid_bias
            if score > myd_best:
                myd_best = score
                oppd_best = opd
        # Penalty for being too close to the opponent to avoid immediate interception
        close_pen = 0.05 * dist(px, py, ox, oy)
        return myd_best - close_pen

    # Deterministic tie-break: fixed ordering already in moves list
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        val = position_value(nx, ny)
        # Additional certainty: if we land closer than opponent to some resource, prefer over general movement
        if val > best_val:
            best_val = val
            best_move = (dx if (sx + dx, sy + dy) == (nx, ny) else 0, dy if (sx + dx, sy + dy) == (nx, ny) else 0)

    return [int(best_move[0]), int(best_move[1])]