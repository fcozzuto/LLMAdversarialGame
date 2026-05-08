def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obstacles_list)
    resources = observation.get("resources", []) or []

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def legal_neighbors():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    yield dx, dy, nx, ny

    nbrs = list(legal_neighbors())
    if not nbrs:
        return [0, 0]

    center = (w - 1) / 2.0, (h - 1) / 2.0

    if resources:
        tx, ty = min((tuple(r) for r in resources), key=lambda p: man(sx, sy, p[0], p[1]))
        scored = []
        for dx, dy, nx, ny in nbrs:
            d = man(nx, ny, tx, ty)
            scored.append((d, man(nx, ny, ox, oy), dx, dy))
        scored.sort()
        return [scored[0][2], scored[0][3]]

    # No visible resources: keep distance from opponent; drift to center as tie-breaker.
    scored = []
    for dx, dy, nx, ny in nbrs:
        dist_op = man(nx, ny, ox, oy)
        dc = abs(nx - center[0]) + abs(ny - center[1])
        scored.append((-dist_op, dc, dx, dy))
    scored.sort()
    return [scored[0][2], scored[0][3]]