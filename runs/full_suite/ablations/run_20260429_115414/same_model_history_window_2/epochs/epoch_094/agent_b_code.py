def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            d_to_opp = cheb(nx, ny, ox, oy)
            if best is None or d_to_opp > best[0]:
                best = (d_to_opp, dx, dy)
        return [best[1], best[2]]

    best_res = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer than opponent, and not too far overall.
        val = (do - ds) * 3 - ds
        # If we're facing a likely blocked immediate step toward it, discourage slightly.
        stepx = 0 if rx == sx else (1 if rx > sx else -1)
        stepy = 0 if ry == sy else (1 if ry > sy else -1)
        nx, ny = sx + stepx, sy + stepy
        if not ok(nx, ny):
            val -= 5
        if best_val is None or val > best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res
    best = None
    for dx, dy, nx, ny in legal:
        d_now = cheb(sx, sy, tx, ty)
        d_new = cheb(nx, ny, tx, ty)
        # Primary: reduce distance to target. Secondary: pull away from opponent.
        improve = d_now - d_new
        d_to_opp = cheb(nx, ny, ox, oy)
        # Tertiary: avoid stepping into squares adjacent to obstacles (mildly).
        adj_block = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if (ax, ay) in blocked:
                    adj_block += 1
        key = (improve, d_to_opp, -adj_block, -abs((nx - tx)) - abs((ny - ty)))
        if best is None or key > best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]