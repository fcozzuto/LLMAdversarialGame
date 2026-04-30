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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        d = a - b
        if d < 0: d = -d
        return d

    def cheb(ax, ay, bx, by):
        dx = dist(ax, bx)
        dy = dist(ay, by)
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    if resources:
        tx, ty = min(resources, key=lambda p: (cheb(p[0], p[1], ox, oy), cheb(p[0], p[1], sx, sy), p[0], p[1]))
        target = (tx, ty)

    if target:
        tx, ty = target
        best = None
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = (cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), nx, ny, dx, dy)
            if best is None or v < bestv:
                best = (dx, dy)
                bestv = v
        if best is not None:
            return [int(best[0]), int(best[1])]

    # No resource or no valid move: move away from opponent if possible
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # maximize distance from opponent
        v = (-cheb(nx, ny, ox, oy), nx, ny, dx, dy)
        if best is None or v < bestv:
            best = (dx, dy)
            bestv = v
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]