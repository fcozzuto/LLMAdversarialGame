def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set and (sx, sy) not in obstacles:
        return [0, 0]

    if not resources:
        # With nothing to collect, head to the corner farthest from opponent.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_corner = None
        best_val = -10**9
        for cx, cy in corners:
            val = (abs(cx - ox) + abs(cy - oy), -abs(cx - sx) - abs(cy - sy))
            if val > (best_val, -10**9):
                best_val = val[0]
                best_corner = (cx, cy)
        tx, ty = best_corner
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obstacles or not inb(sx + dx, sy + dy):
            # fall back to any legal move that reduces manhattan distance to target
            best = None
            bestd = 10**9
            for adx, ady in legal:
                nx, ny = sx + adx, sy + ady
                d = abs(nx - tx) + abs(ny - ty)
                if d < bestd or (d == bestd and (adx, ady) < best):
                    bestd = d
                    best = (adx, ady)
            return [best[0], best[1]]
        return [dx, dy]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a target resource that maximizes the advantage swing vs opponent.
    best_target = None
    best_key = (-10**9, 10**9)  # (opp_self_gap, -self_dist)
    for rx, ry in res_set:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        key = (od - sd, sd)
        if key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Prefer immediate collection; otherwise minimize self distance to chosen target
    # with a small bias to increase opponent distance.
    best_move = None
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in res_set:
            return [dx, dy]
        sd2 = md(nx, ny, tx, ty)
        od2 = md(ox, oy, tx, ty)
        # Prefer reduced distance, and if tie, prefer keeping opponent farther from target.
        score = (-sd2, od2, dx, dy)
        if best_move is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]