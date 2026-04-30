def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            if legal(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_t = None
        best_key = None
        for (rx, ry) in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            key = (myd - 0.35 * opd, ry, rx)  # race: smaller my distance; prefer where I'm relatively closer
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        if not legal(tx, ty):
            tx, ty = ox, oy

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        # Seek target quickly; also keep some separation from opponent to reduce contention
        val = (-myd * 10) + (opd * 0.2)
        # Small deterministic tie-breaker to reduce oscillation:
        val_key = (val, -cheb(nx, ny, sx, sy), dy, dx)
        if best_val is None or val_key > best_val:
            best_val = val_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]