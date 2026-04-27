def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**9

    for dx, dy in dirs:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # nearest resource distance (prefer approaching)
        if resources:
            mr = min(cheb((nx, ny), r) for r in resources)
        else:
            mr = 50
        # distance to opponent (prefer separating)
        mo = cheb((nx, ny), (ox, oy))
        # small penalty near obstacles
        adj = 0
        for ax, ay in dirs:
            if ax == 0 and ay == 0:
                continue
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obs:
                adj += 1
        v = (-mr) + 0.35 * mo - 0.12 * adj
        if v > bestv or (v == bestv and best is not None and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]