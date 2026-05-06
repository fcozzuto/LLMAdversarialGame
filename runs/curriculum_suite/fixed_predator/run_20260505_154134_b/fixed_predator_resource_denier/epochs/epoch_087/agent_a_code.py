def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        for dx, dy, nx, ny in legal:
            myd = 10**9
            opd = 10**9
            for r in resources:
                if isinstance(r, (list, tuple)) and len(r) >= 2:
                    rx, ry = int(r[0]), int(r[1])
                    d1 = cheb(nx, ny, rx, ry)
                    if d1 < myd:
                        myd = d1
                    d2 = cheb(ox, oy, rx, ry)
                    if d2 < opd:
                        opd = d2
            score = (myd - opd, myd, nx + 2 * ny, dx, dy)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]
    else:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, tx, ty)
            score = (d, nx + ny, dx, dy)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]