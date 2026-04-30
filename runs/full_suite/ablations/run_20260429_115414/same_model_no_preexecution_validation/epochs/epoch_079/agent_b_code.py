def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            return [dx, dy]
        best = (0, 0)
        best_v = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = cheb(nx, ny, tx, ty) - 0.2 * cheb(nx, ny, ox, oy)
            if best_v is None or v < best_v:
                best_v = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_t = resources[0]
    best_val = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        val = d_me - 0.95 * d_op + 0.01 * (abs(rx - (w - 1)) + abs(ry - (h - 1)))
        if best_val is None or val < best_val:
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t
    primary_dx = 0 if tx == sx else (1 if tx > sx else -1)
    primary_dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + primary_dx, sy + primary_dy
    if inside(nx, ny):
        return [primary_dx, primary_dy]

    best = (0, 0)
    best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = cheb(nx, ny, tx, ty) - 0.95 * cheb(nx, ny, ox, oy) + 0.001 * cheb(nx, ny, w // 2, h // 2)
        if best_v is None or v < best_v:
            best_v = v
            best = (dx, dy)
    return [best[0], best[1]]