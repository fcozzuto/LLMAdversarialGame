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

    def ok(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        bestm, bestv = (0, 0), -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    best = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Score: prefer resources I'm closer to, then closer overall, then corner bias (deterministic).
        key = (-(myd - opd), myd, -((tx == W - 1) and (ty == H - 1)), -((tx == W - 1) or (ty == H - 1)), tx, ty)
        # Minimize key lexicographically; invert first component via negative to keep "closer than opponent" priority.
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    curd = cheb(sx, sy, tx, ty)
    bestm, bestv = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        od = cheb(nx, ny, ox, oy)
        # Prefer stepping that reduces distance to target; if equal, push away opponent and avoid getting stuck.
        v = (curd - nd) * 1000 + od - nd * 2
        if nx == tx and ny == ty:
            v += 10**6
        if v > bestv:
            bestv, bestm = v, (dx, dy)
    return [bestm[0], bestm[1]]