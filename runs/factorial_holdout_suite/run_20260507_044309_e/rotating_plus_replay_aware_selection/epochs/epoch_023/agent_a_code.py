def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    if not resources:
        cx, cy = w // 2, h // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        if (sx + dx, sy + dy) in obstacles:
            dx, dy = (dx, 0) if (sx + dx, sy) not in obstacles else (0, dy)
            if (sx + dx, sy + dy) in obstacles: dx, dy = 0, 0
        return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_key = None
    cx, cy = w // 2, h // 2
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach not later than opponent; otherwise heavily penalize.
        lead = do - ds  # positive => we are earlier
        own_center = cheb(rx, ry, cx, cy)
        risk = (ds + 2 * own_center)  # keep movement purposeful, not zig-zag
        key = (0 if lead >= 0 else 1, -lead if lead >= 0 else lead, risk, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    # If blocked, try all 8 directions + stay, pick best deterministic move toward target.
    if not valid(sx + dx, sy + dy):
        moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        bestm = (0, 0)
        bestmk = None
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not valid(nx, ny):
                continue
            # Prefer decreasing chebyshev distance to target; tie-break by opponent distance too.
            d = cheb(nx, ny, tx, ty)
            od = cheb(nx, ny, ox, oy)
            mk = (d, -od, mx, my)
            if bestmk is None or mk < bestmk:
                bestmk = mk
                bestm = (mx, my)
        return [bestm[0], bestm[1]]

    return [dx, dy]