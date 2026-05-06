def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_key = None

    if not resources:
        tx, ty = ox, oy
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            key = (-d, dx, dy)
            if best_key is None or key > best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Score: prefer moves that beat opponent to some resource; slight tie-break by closer resource.
        local_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (do - ds, -ds, -(rx * 1000 + ry))
            if local_best is None or key > local_best:
                local_best = key
        if local_best is None:
            continue
        if best_key is None or local_best > best_key:
            best_key, best = local_best, (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]