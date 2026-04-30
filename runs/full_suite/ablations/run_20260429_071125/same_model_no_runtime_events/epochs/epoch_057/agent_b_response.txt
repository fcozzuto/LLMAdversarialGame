def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if res:
        best_t = None
        best_key = None
        for tx, ty in res:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer resources where we are closer than opponent; if none, minimize advantage deficit.
            key = (ds - do, ds, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, tx, ty)
        # Encourage moving off opponent's direct pressure; reward immediate landing on a resource.
        landed = 1 if (nx, ny) in set(res) else 0
        do = cheb(nx, ny, ox, oy)
        val = (-d, -landed, do, nx, ny)  # deterministic tie-break via nx,ny
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]