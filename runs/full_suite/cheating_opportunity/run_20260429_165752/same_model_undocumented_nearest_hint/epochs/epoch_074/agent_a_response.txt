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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (W - 1) // 2, (H - 1) // 2
    if not resources:
        bestm = (0, 0)
        bests = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            sd = cheb(nx, ny, cx, cy)
            opd = cheb(nx, ny, ox, oy)
            score = -sd + 0.08 * opd
            if score > bests:
                bests, bestm = score, (dx, dy)
        return [bestm[0], bestm[1]]

    # Choose a target resource we are likely to reach first.
    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        key = (sd - opd, sd, tx, ty)
        if best_key is None or key < best_key:
            best_key, best_t = key, (tx, ty)
    tx, ty = best_t

    bestm = (0, 0)
    bests = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(nx, ny, ox, oy)
        prog = cheb(nx, ny, cx, cy) - cheb(sx, sy, cx, cy)
        score = -sd2 + 0.12 * opd2 - 0.02 * prog
        if score > bests:
            bests, bestm = score, (dx, dy)
    return [bestm[0], bestm[1]]