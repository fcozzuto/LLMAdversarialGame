def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    sr = (observation.get("self_role") or "").lower()
    pr = (observation.get("opponent_role") or "").lower()
    self_purs = any(k in sr for k in ("purs", "catch", "hunt", "chaser", "pursuer"))
    opp_purs = any(k in pr for k in ("purs", "catch", "hunt", "chaser", "pursuer"))
    pursuer = self_purs and not (opp_purs and not self_purs)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    obs_list = list(obs)
    def clearance(x, y):
        if not obs_list:
            return 6
        m = 10
        for (ox2, oy2) in obs_list:
            d = abs(x - ox2) + abs(y - oy2)
            if d < m:
                m = d
        return m

    best = (0, 0)
    best_val = None

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = dist2(nx, ny)
        c = clearance(nx, ny)
        # tie-breakers are deterministic via iteration order
        if pursuer:
            val = (-d, c)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            val = (d, c)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]