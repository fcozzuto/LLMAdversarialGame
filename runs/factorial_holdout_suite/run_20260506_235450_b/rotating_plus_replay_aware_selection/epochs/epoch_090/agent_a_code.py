def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = (int(sp[0]), int(sp[1])) if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = (int(op[0]), int(op[1])) if isinstance(op, (list, tuple)) and len(op) >= 2 else (0, 0)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = observation.get("resources") or []
    resources = []
    for r in res:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            dmin = 10**9
            for rx, ry in resources:
                d = mdist(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            score = -dmin - 0.1 * mdist(nx, ny, ox, oy)
            if score > bestv:
                bestv = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best else [0, 0]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = max(corners, key=lambda c: (mdist(c[0], c[1], sx, sy), -mdist(c[0], c[1], ox, oy)))
    best = None
    bestv = -10**18
    for dx, dy, nx, ny in legal:
        v = -mdist(nx, ny, cx, cy) + 0.05 * mdist(nx, ny, ox, oy)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])] if best else [0, 0]