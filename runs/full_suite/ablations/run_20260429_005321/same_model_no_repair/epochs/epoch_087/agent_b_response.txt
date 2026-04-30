def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = ((w - 1) // 2, (h - 1) // 2) if (sx + sy) % 2 == 0 else (w - 1 - ((w - 1) // 2), h - 1 - ((h - 1) // 2))
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, tx, ty)
            k = (d, dx, dy)
            if best is None or k < best[0]:
                best = (k, (dx, dy))
        return [best[1][0], best[1][1]]

    rlist = [(r[0], r[1]) for r in resources]
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        # Prefer moves that are closer to some resource than the opponent would be.
        best = None
        for rx, ry in rlist:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # if we reach the resource now, huge priority
            if myd == 0:
                score = (-10**9, 0, 0)
            else:
                # Encourage "tempo": beating opponent on that resource
                delta = opd - myd
                # If delta small, also prefer overall closeness
                score = (-(delta * 10 + myd), myd, cheb(nx, ny, (rx + ox) // 2, (ry + oy) // 2))
            if best is None or score < best:
                best = score
        # Break ties deterministically by moving in lexicographic order of (dx,dy)
        key = (best, dx, dy, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]