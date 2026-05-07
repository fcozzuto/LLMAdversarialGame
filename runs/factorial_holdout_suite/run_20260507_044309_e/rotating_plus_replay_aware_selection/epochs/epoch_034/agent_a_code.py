def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        return None

    if not resources:
        tx, ty = w // 2, h // 2
        for dx, dy in ((1, 1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (-1, -1), (0, 0)):
            ndx = 0 if tx == sx else (1 if tx > sx else -1)
            ndy = 0 if ty == sy else (1 if ty > sy else -1)
            # bias toward center direction, but check legality
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        for adx, ady in ((dx, dy), (dx, 0), (0, dy), (0, 0)):
            r = clamp_move(adx, ady)
            if r is not None:
                return r
        return [0, 0]

    best = None
    bestv = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive => we reach earlier (assuming similar rules)
        center = cheb(rx, ry, w // 2, h // 2)
        # Deterministic scoring: prefer earlier lead, then closer, then center-regularization
        v = lead * 10000 - ds * 7 - center
        if v > bestv:
            bestv = v
            best = (rx, ry)

    rx, ry = best
    dx = 0 if sx == rx else (1 if rx > sx else -1)
    dy = 0 if sy == ry else (1 if ry > sy else -1)

    # Preferred: diagonal toward target, then axis-aligned, then stay.
    for adx, ady in ((dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)):
        r = clamp_move(adx, ady)
        if r is not None:
            return r

    # Fallback: any legal move toward reducing chebyshev distance; deterministic tie-break by move order.
    move_order = [(0, 0), (1, 1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (-1, -1)]
    curd = cheb(sx, sy, rx, ry)
    bestd = curd
    bestm = [0, 0]
    for mdx, mdy in move_order:
        nx, ny = sx + mdx, sy + mdy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, rx, ry)
        if d < bestd:
            bestd = d
            bestm = [mdx, mdy]
    return bestm