def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        best_r = None
        best_d = None
        for rx, ry in resources:
            if (rx, ry) == (sx, sy):
                continue
            d = manh(sx, sy, rx, ry)
            if best_d is None or d < best_d:
                best_d = d
                best_r = (rx, ry)
        if best_r is not None:
            tx, ty = best_r
            best = None
            for dx, dy, nx, ny in legal:
                d2 = manh(nx, ny, tx, ty)
                if best is None or d2 < best:
                    best = d2
                    best_move = (dx, dy)
            return [best_move[0], best_move[1]]

    if (ox, oy) != (sx, sy):
        best = None
        best_mv = (0, 0)
        for dx, dy, nx, ny in legal:
            d = manh(nx, ny, ox, oy)
            if best is None or d < best:
                best = d
                best_mv = (dx, dy)
        return [best_mv[0], best_mv[1]]

    return [0, 0]