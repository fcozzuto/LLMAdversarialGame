def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    w = int(w)
    h = int(h)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        best_t = resources[0]
        best_s = None
        for rx, ry in resources:
            ds = cheb(rx, ry, sx, sy)
            do = cheb(rx, ry, ox, oy)
            s = do - ds
            if best_s is None or s > best_s or (s == best_s and (ds < cheb(best_t[0], best_t[1], sx, sy) or (ds == cheb(best_t[0], best_t[1], sx, sy) and (rx, ry) < best_t))):
                best_s = s
                best_t = (rx, ry)
        tx, ty = best_t
        best_m = (0, 0)
        best_v = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - 0.01 * cheb(nx, ny, ox, oy)
            if v > best_v or (v == best_v and (dx, dy) < best_m):
                best_v = v
                best_m = (dx, dy)
        return [int(best_m[0]), int(best_m[1])]
    else:
        tx, ty = w // 2, h // 2
        best_m = (0, 0)
        best_v = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - 0.02 * cheb(nx, ny, ox, oy)
            if v > best_v or (v == best_v and (dx, dy) < best_m):
                best_v = v
                best_m = (dx, dy