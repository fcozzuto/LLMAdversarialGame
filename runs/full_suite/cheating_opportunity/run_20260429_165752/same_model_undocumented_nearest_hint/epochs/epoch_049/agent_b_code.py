def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    best = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer resources I'm closer to than opponent
        key = (myd - opd, myd, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    best_move = (10**9, 10**9, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            myd2 = cheb(nx, ny, tx, ty)
            # also keep stepping where opponent is relatively disadvantaged
            opd2 = cheb(ox, oy, tx, ty)
            tie = cheb(nx, ny, ox, oy)
            key = (myd2 - opd2, myd2, tie, dx * 10 + dy)
            if key < best_move:
                best_move = key
                best_dx, best_dy = dx, dy

    return [best_dx, best_dy]