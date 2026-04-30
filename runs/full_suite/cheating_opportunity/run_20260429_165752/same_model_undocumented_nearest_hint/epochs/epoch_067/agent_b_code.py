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

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    if resources:
        bestd = 10**9
        best = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                best = (rx, ry)
            elif d == bestd and (rx, ry) < best:
                best = (rx, ry)
        target = best
    else:
        target = (W // 2, H // 2)

    bx = by = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            d_self = cheb(nx, ny, target[0], target[1])
            d_opp = cheb(nx, ny, ox, oy)
            score = -d_self + 0.05 * d_opp
        else:
            d_self = cheb(nx, ny, target[0], target[1])
            score = -d_self
        if score > best_score:
            best_score = score
            bx, by = dx, dy
        elif score == best_score and (dx, dy) < (bx, by):
            bx, by = dx, dy

    if bx is None:
        bx, by = 0, 0
    return [int(bx), int(by)]