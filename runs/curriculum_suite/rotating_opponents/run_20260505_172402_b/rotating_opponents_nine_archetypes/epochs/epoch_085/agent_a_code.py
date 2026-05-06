def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not valid(sx, sy):
        found = False
        for yy in range(h):
            for xx in range(w):
                if valid(xx, yy):
                    sx, sy = xx, yy
                    found = True
                    break
            if found:
                break

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    bestv = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if resources:
                dres = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
                target = -dres
            else:
                target = -cheb(nx, ny, cx, cy)
            dopp = cheb(nx, ny, ox, oy)
            threat = 0
            if dops := dopp <= 1:
                threat = -100  # avoid adjacency if possible
            elif dopp <= 2:
                threat = dopp * 2
            val = target + threat + (dopp * 0.1)
            if bestv is None or val > bestv or (val == bestv and (dx, dy) < best):
                bestv = val
                best = (dx, dy)

    if best is None:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if valid(nx, ny):
                    return [dx, dy]
        return [0, 0]
    return [int(best[0]), int(best[1])]