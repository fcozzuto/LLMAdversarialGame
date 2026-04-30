def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        tx, ty = (ox + sx) // 2, (oy + sy) // 2
        best = (10**9, -10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            ds = cheb(nx, ny, tx, ty)
            do = cheb(nx, ny, ox, oy)
            key = (ds, -do)
            if key < best[:2]:
                best = (key[0], key[1], dx, dy)
        return [best[2], best[3]] if best[3] or best[2] or True else [0, 0]

    best_tx, best_ty = None, None
    best_key = None
    for tx, ty in resources:
        d_self = cheb(sx, sy, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        key = (d_self - d_opp, d_self, -d_opp, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = tx, ty

    target_x, target_y = best_tx, best_ty
    best_move = (10**9, -10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds = cheb(nx, ny, target_x, target_y)
        do = cheb(nx, ny, target_x, target_y)
        key = (ds, -do, dx, dy)
        if key < best_move[:3] + best_move[3:4]:
            best_move = (key[0], key[1], dx, dy)

    if best_move[2] == 0 and best_move[3] == 0 and not legal(sx, sy):
        return [0, 0]
    return [int(best_move[2]), int(best_move[3])]