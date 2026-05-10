def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds
        key = (margin, -ds, -((rx + ry) % 7))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Strongly prefer steps that reduce our distance to target and don't run adjacent to obstacles.
        ds2 = cheb(nx, ny, tx, ty)
        cur = (cheb(ox, oy, tx, ty) - ds2) * 1000 - ds2
        # Obstacle adjacency penalty
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if 0 <= x2 < w and 0 <= y2 < h and (x2, y2) in obs:
                    pen += 1
        cur -= pen * 3
        # Small deterministic tie-break toward increasing coordinates
        cur += (dx + 1) * 0.01 + (dy + 1) * 0.001
        if cur > bestv:
            bestv = cur
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]