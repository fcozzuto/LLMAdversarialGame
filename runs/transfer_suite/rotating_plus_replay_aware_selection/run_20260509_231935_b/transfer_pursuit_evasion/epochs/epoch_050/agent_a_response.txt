def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opp_role and ("pursuer" in self_role or "pursuit" in self_role))
    is_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role)

    dir_mult = 1
    if is_pursuer:
        dir_mult = -1  # minimize distance
    elif is_evader:
        dir_mult = 1   # maximize distance

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    obstacles = list(obs)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def min_obstacle_dist2(nx, ny):
        if not obstacles:
            return 999999
        md = 999999
        for ax, ay in obstacles:
            dx, dy = nx - ax, ny - ay
            d2 = dx * dx + dy * dy
            if d2 < md:
                md = d2
        return md

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = dir_mult * d2
        # tie-break: prefer staying toward/away from center depending on role
        center_pen = ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) ** 0.5
        score += (-0.03 * center_pen) if is_pursuer else (0.03 * center_pen)
        # obstacle avoidance: keep away when evading, slightly avoid when pursuing
        od2 = min_obstacle_dist2(nx, ny)
        if is_evader:
            score += 0.05 * (od2 ** 0.5)
        else:
            score += 0.02 * (od2 ** 0.5)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]