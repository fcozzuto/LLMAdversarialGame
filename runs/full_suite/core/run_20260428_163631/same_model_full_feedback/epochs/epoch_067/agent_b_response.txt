def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_adj(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    c += 1
        return c

    def best_target(px, py):
        if not resources:
            return (w // 2, h // 2)
        best = None
        bestv = -10**18
        for rx, ry in resources:
            if not ok(px, py):
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            v = (do - ds) * 100 - ds  # maximize being closer than opponent, then minimize distance
            if v > bestv:
                bestv = v
                best = (rx, ry)
        if best is None:
            best = min(resources, key=lambda r: cheb(px, py, r[0], r[1]))
        return best

    tx, ty = best_target(sx, sy)

    best_move = (0, 0)
    best_val = -10**18
    center = (w // 2, h // 2)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        v = (do - ds) * 100 - ds
        v -= obst_adj(nx, ny) * 3
        # If already targeting is poor, gently drift to center to access more resources
        v -= cheb(nx, ny, center[0], center[1]) * 0.1
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    if not ok(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]