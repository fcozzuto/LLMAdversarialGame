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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = (0, 0)
    best_score = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_op = cheb(nx, ny, ox, oy)
            d_near = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < d_near:
                    d_near = d
            score = 1000 - d_near + 0.2 * d_op
            if score > best_score:
                best_score = score
                best = [dx, dy]
        return [int(best[0]), int(best[1])]

    cx, cy = (W - 1) // 2, (H - 1) // 2
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_from_op = cheb(nx, ny, ox, oy)
        d_to_center = cheb(nx, ny, cx, cy)
        score = 2.0 * d_from_op - 0.1 * d_to_center
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return [int(best[0]), int(best[1])]