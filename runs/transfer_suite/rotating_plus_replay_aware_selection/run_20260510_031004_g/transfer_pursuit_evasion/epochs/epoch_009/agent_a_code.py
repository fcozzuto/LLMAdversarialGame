def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or ("evade" in self_role)
    if not is_evader:
        # If roles are ambiguous, assume we are pursuer unless explicitly stated otherwise.
        if "evader" in opponent_role and ("pursuer" in self_role or "pursuit" in self_role or "hunter" in self_role):
            is_evader = False

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    center_x = (w - 1) // 2
    center_y = (h - 1) // 2

    best_dxdy = [0, 0]
    if is_evader:
        best_score = -10**9
    else:
        best_score = 10**9

    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                dist = md(nx, ny, ox, oy)
                # Small deterministic bias: prefer staying closer to center when tied (keeps mobility).
                cen = md(nx, ny, center_x, center_y)
                # Extra bias: avoid moving away too much in a straight line (helps cornering as pursuer).
                line_bias = 0
                if dx != 0 or dy != 0:
                    if (nx - ox) * (sx - ox) >= 0 and (ny - oy) * (sy - oy) >= 0:
                        line_bias = 1
                if is_evader:
                    score = dist * 100 - cen - line_bias
                    if score > best_score:
                        best_score = score
                        best_dxdy = [dx, dy]
                else:
                    score = -dist * 100 - cen - line_bias
                    if score > best_score:
                        best_score = score
                        best_dxdy = [dx, dy]

    return best_dxdy