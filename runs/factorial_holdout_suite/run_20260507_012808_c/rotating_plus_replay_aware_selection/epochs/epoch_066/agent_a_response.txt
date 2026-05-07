def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    def clamp_step(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return clamp_step(tx, ty)

    res = [tuple(r) for r in resources]
    cand_best = (None, -10**9, -10**9, 10**9)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_margin = -10**9
        best_self = 10**9
        best_opp = 10**9
        margin_list = []

        for rx, ry in res:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            m = do - ds
            margin_list.append(m)
            if m > best_margin or (m == best_margin and (ds < best_self or (ds == best_self and do < best_opp))):
                best_margin, best_self, best_opp = m, ds, do

        # Favor grabbing first (higher best_margin), but also prefer moving closer to "contested" resources.
        # Deterministic tie-breakers: higher best_opp-self gap, then smaller best_self, then larger opponent worst-case.
        worst_margin = min(margin_list) if margin_list else 0
        score1 = best_margin
        score2 = worst_margin

        key = (dx, dy)
        # Compare: maximize score1, then maximize score2, then minimize best_self, then maximize (best_opp - best_self)
        cur = (score1, score2, -best_self, best_opp - best_self)
        best = cand_best[0]
        if best is None or cur > cand_best[1:]:
            cand_best = (key, score1, score2, -best_self)

    return [cand_best[0][0], cand_best[0][1]]