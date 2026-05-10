def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("evader" not in self_role and "pursuer" not in opp_role)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    obs_list = list(obs)

    def obs_pen(nx, ny):
        p = 0
        for ox2, oy2 in obs_list:
            d = abs(nx - ox2) + abs(ny - oy2)
            if d == 0:
                return 1000
            if d == 1:
                p += 4
            elif d == 2:
                p += 1
        return p

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy

        if i_am_pursuer:
            # chase: minimize distance to opponent
            score = d2 - 0.25 * obs_pen(nx, ny)
            # tie-break: prefer moves that reduce Chebyshev distance
            cheb = max(abs(nx - ox), abs(ny - oy))
            score += 0.001 * cheb
        else:
            # evade: maximize distance from opponent, avoid corners/walls
            score = -d2 - 0.25 * obs_pen(nx, ny)
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            cb = min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            score += -0.02 * cb  # smaller cb is worse; negative encourages away from corners

        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best