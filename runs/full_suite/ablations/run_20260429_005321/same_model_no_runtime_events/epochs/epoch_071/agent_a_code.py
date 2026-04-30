def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    if resources:
        best = None
        bestv = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            dmin = None
            for rx, ry in resources:
                dv = dist(nx, ny, rx, ry)
                if dmin is None or dv < dmin:
                    dmin = dv
            v = (dmin, -dist(nx, ny, ox, oy), dirs.index((dx, dy)))
            if best is None or v < bestv:
                best = (dx, dy)
                bestv = v
        return [int(best[0]), int(best[1])]

    tx, ty = (w - 1) // 2, (h - 1) // 2
    best = None
    bestv = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        v = (dist(nx, ny, tx, ty), -dist(nx, ny, ox, oy), dirs.index((dx, dy)))
        if best is None or v < bestv:
            best = (dx, dy)
            bestv = v
    return [int(best[0]), int(best[1])]