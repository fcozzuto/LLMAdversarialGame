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

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(dx, dy):
        return inside(sx + dx, sy + dy)

    if resources:
        best = None
        for dx, dy in moves:
            if not legal(dx, dy):
                continue
            nx, ny = sx + dx, sy + dy
            best_r = None
            best_d = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < best_d:
                    best_d = d
                    best_r = (rx, ry)
            if best is None or best_d < best[0]:
                best = (best_d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # No resources: step away from opponent, prefer staying if blocked
    best = None
    for dx, dy in moves:
        if not legal(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, ox, oy)
        if best is None or d > best[0]:
            best = (d, dx, dy)
    return [best[1], best[2]] if best else [0, 0]