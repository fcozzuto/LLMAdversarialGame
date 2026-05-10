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

    def edge_bias(nx, ny):
        # Prefer staying on the edge away from center (helps deterministic escape routes)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return abs(nx - cx) + abs(ny - cy)

    def obst_pen(nx, ny):
        if (nx, ny) in obs:
            return 1e6
        p = 0
        for (ex, ey) in obs:
            d = abs(nx - ex) + abs(ny - ey)
            if d == 0:
                return 1e6
            if d == 1:
                p += 6
            elif d == 2:
                p += 2
        return p

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        md = abs(nx - ox) + abs(ny - oy)
        pen = obst_pen(nx, ny)

        if i_am_pursuer:
            # Chase while avoiding getting too close to obstacles.
            score = (-md) + (2.0 if md <= 1 else 0.0) - 0.25 * pen
        else:
            # Flee: maximize distance, bias toward far edge, penalize obstacle proximity.
            score = (md) + 0.35 * edge_bias(nx, ny) - 0.5 * pen
            # If currently adjacent, try to break separation immediately.
            if abs(sx - ox) + abs(sy - oy) <= 1 and md < 2:
                score -= 2.0

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]