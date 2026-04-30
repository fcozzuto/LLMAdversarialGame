def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy)]

    if not resources:
        tx, ty = (w // 2, h // 2)
        if cheb(sx, sy, ox, oy) < 2:
            tx, ty = (0 if sx > ox else w - 1, 0 if sy > oy else h - 1)
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (cheb(nx, ny, tx, ty), -cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [int(best[1]), int(best[2])]

    best_r = None
    best_key = None
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        key = (-(dO - dS), dS, rx, ry)  # prefer being closer than opponent; then closer to self
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        dT = cheb(nx, ny, rx, ry)
        dO = cheb(nx, ny, ox, oy)
        key = (dT, -dO, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [int(best[1]), int(best[2])]