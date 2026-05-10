def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not res:
        for dx, dy in dirs:
            nx, ny = int(sx) + dx, int(sy) + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    for dx, dy in dirs:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dmin = 10**9
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            if d < dmin:
                dmin = d
        dobj = cheb(nx, ny, int(ox), int(oy))
        cand = (dmin, -dobj, abs(dx) + abs(dy), dx, dy)
        if best is None or cand < best:
            best = cand
    if best is None:
        return [0, 0]
    return [best[3], best[4]]