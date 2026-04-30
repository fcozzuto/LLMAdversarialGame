def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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

    def free(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = ox, oy
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    myfast = []
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if myd <= opd:
            myfast.append((rx, ry, myd, opd))
    candidates = myfast if myfast else [(rx, ry, cheb(sx, sy, rx, ry), cheb(ox, oy, rx, ry)) for rx, ry in resources]

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if candidates:
            best_res_val = -10**9
            for rx, ry, myd0, opd0 in candidates:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                takeover = 2 if myd <= opd else 0
                v = takeover * 1000 - myd * 3 + (myd0 == myd) * 1 - cheb(nx, ny, ox, oy)
                if v > best_res_val:
                    best_res_val = v
            val = best_res_val
        else:
            val = -cheb(nx, ny, ox, oy)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]