def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                res.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_block_pen(x, y):
        p = 0
        for ddx, ddy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
            nx, ny = x + ddx, y + ddy
            if (nx, ny) in obstacles:
                p += 1
        return p

    def valid_moves_from(x, y):
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    out.append((dx, dy, nx, ny))
        return out

    if res:
        best = None
        for rx, ry in res:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            target_score = (do - ds) * 10 - adj_block_pen(rx, ry) * 2
            tie = rx + ry * 0.01
            val = (-(target_score), tie)  # deterministic min
            if best is None or val < best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = w // 2, h // 2

    moves = valid_moves_from(sx, sy)
    if not moves:
        return [0, 0]

    cur_on_resource = (sx, sy) in obstacles
    bestm = None
    for dx, dy, nx, ny in moves:
        dself = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer reducing our distance while keeping opponent lagging.
        score = (do - dself) * 10 - dself - adj_block_pen(nx, ny) * 3
        # Small deterministic tie-break favoring progress toward target.
        tb = (nx - sx) * 0.001 + (ny - sy) * 0.0001 + (nx * 0.000001 + ny * 0.0000001)
        val = (-score, tb, dx, dy)
        if bestm is None or val < bestm[0]:
            bestm = (val, dx, dy)

    return [int(bestm[1]), int(bestm[2])]