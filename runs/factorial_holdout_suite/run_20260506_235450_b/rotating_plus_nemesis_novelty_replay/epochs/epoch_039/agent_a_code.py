def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    resources = observation.get("resources", None) or []
    obstacles = observation.get("obstacles", None) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    if not resources:
        tx, ty = (w - 1, h - 1)
        if (ox, oy) == (tx, ty):
            tx, ty = (0, h - 1 if h else 0)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -dist2((nx, ny), (tx, ty)) - 0.2 * dist2((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = 10**18
        d_opp = 10**18
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                d_self = min(d_self, dist2((nx, ny), (rx, ry)))
                d_opp = min(d_opp, dist2((ox, oy), (rx, ry)))
        v = -d_self
        if d_opp < d_self:
            v -= 0.5 * (d_self - d_opp)
        if (nx, ny) == (ox, oy):
            v += 1e6
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]