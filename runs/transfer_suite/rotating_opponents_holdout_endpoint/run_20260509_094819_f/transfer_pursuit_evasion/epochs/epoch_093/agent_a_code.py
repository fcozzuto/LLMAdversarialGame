def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    sr = str(observation.get("self_role") or "")
    pursuer = ("pursur" in sr.lower()) or ("chaser" in sr.lower()) or ("hunter" in sr.lower())

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked_pen(x, y):
        if (x, y) in blocked:
            return 10**6
        p = 0
        for bx, by in blocked:
            d = cheb(x, y, bx, by)
            if d == 0:
                return 10**6
            if d == 1:
                p += 2
        return p

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if pursuer:
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            v = cheb(nx, ny, ox, oy) + blocked_pen(nx, ny)
            v += 0.001 if (dx == 0 and dy == 0) else 0.0
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    else:
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        tx, ty = target
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            v = -cheb(nx, ny, ox, oy)  # maximize distance => minimize negative
            v += 0.1 * cheb(nx, ny, tx, ty)  # drift toward far corner
            v += 0.5 * blocked_pen(nx, ny)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]