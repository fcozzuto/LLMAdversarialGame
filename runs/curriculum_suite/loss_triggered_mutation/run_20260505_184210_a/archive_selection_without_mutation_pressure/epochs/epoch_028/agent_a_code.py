def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    if not resources:
        # Drift away from opponent a bit, favoring edge toward resources-less corner.
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)
            # Prefer staying closer to center to reduce being boxed in by patrol.
            center = (w - 1) / 2.0, (h - 1) / 2.0
            cx, cy = center
            tie = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            val = (v, tie)
            if bestv is None or val > bestv:
                bestv, best = val, [dx, dy]
        return best

    # Choose move that maximizes our reach advantage after the move,
    # but avoids moves that let opponent win an immediate nearby resource.
    best_move = None
    best_score = None
    opp_d0 = cheb(sx, sy, ox, oy)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # immediate danger: if we can be overtaken on the best target
        best_res_adv = -10**9
        best_res_self = 10**9
        opp_win_risk = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => we are closer after our move
            if adv > best_res_adv or (adv == best_res_adv and ds < best_res_self):
                best_res_adv = adv
                best_res_self = ds
            # Risk if opponent is already at least as close and within 1 step.
            if do <= 1 and do <= ds:
                opp_win_risk += 1

        # Encourage progress (smaller ds) and slightly keep distance unless we are clearly leading.
        dist_self = cheb(nx, ny, ox, oy)
        lead = best_res_adv
        dist_term = dist_self if lead <= 0 else -dist_self
        # If opponent can quickly secure many resources, penalize strongly.
        score = (lead * 1000) - (best_res_self * 3) + dist_term - (opp_win_risk * 500) - (opp_d0 == 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move