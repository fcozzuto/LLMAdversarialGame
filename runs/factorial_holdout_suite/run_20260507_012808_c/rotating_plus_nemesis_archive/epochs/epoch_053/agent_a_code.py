def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    best = None
    best_key = None
    for x, y in res:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        key = (-(od - sd), sd, x, y)  # maximize (od-sd), then minimize sd
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    scored = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd_next = cheb(nx, ny, tx, ty)
        od_next = cheb(ox, oy, tx, ty)
        on_resource = 1 if (nx, ny) == (tx, ty) else 0
        avoid = 0
        # small obstacle pressure: prefer cells with more free neighbors
        free = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if ok(ax, ay):
                free += 1
        avoid -= -free * 0.01  # deterministic bias toward openness
        key = (-on_resource, (od_next - sd_next) * -1, sd_next, -free, nx, ny)
        scored.append((key, [dx, dy]))
    if not scored:
        return [0, 0]
    scored.sort(key=lambda z: z[0])
    return scored[0][1]