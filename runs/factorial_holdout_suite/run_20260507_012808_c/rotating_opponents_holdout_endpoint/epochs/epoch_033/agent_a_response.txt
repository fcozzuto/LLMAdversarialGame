def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = manh(ox, oy, rx, ry)  # opponent uses Manhattan in baseline
        key = (d_op - d_me, -d_me, -abs((w - 1) / 2 - rx) - abs((h - 1) / 2 - ry), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best_move = None
    best_mkey = None
    for dx, dy, nx, ny in moves:
        myd = cheb(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)
        gap = opd - myd
        center_bias = -abs((w - 1) / 2 - nx) - abs((h - 1) / 2 - ny)
        k = (gap, -myd, center_bias, dx, dy)
        if best_mkey is None or k > best_mkey:
            best_mkey = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]