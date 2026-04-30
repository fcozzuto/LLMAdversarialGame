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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        tx, ty = (0, h - 1) if (sx + sy) <= (ox + oy) else (w - 1, 0)
    else:
        # Choose resource where we are relatively closer than opponent (or otherwise deny opponent)
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer: (opponent far) and (we close). Then tie-break toward nearer to center.
            center = cheb(rx, ry, w // 2, h // 2)
            key = (do - ds, -center, -rx - ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        ds1 = cheb(nx, ny, tx, ty)
        do1 = cheb(ox, oy, tx, ty)
        # Main: minimize our distance to chosen target
        # Secondary: keep away from opponent (maximize their distance to our target)
        # Extra: discourage stepping into cells near resources/opponent by using sign-stable heuristic
        opp_prox = cheb(nx, ny, ox, oy)
        score = (-ds1, do1, opp_prox, -abs((nx - (w // 2))) - abs((ny - (h // 2))))
        score = (score[0], score[1], score[2], score[3])
        if best_score == -10**18 or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]