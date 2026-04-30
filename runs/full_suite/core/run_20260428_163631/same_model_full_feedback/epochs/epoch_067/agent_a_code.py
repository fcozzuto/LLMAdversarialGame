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

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources_sorted = sorted(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    near = resources_sorted[0] if resources_sorted else None
    second = resources_sorted[1] if len(resources_sorted) > 1 else None

    best = (0, 0)
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dres = 10**9
        if near is not None:
            dres = cheb(nx, ny, near[0], near[1])
        if second is not None:
            dres2 = cheb(nx, ny, second[0], second[1])
            if dres2 < dres:
                dres = dres2
        dop = cheb(nx, ny, ox, oy)
        sc = (-dres) + (0.15 * dop) - (0.25 * adj_obst(nx, ny))
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
        elif sc == best_sc:
            if (dx, dy) < best:
                best = (dx, dy)
    return [int(best[0]), int(best[1])]