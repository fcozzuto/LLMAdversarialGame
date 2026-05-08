def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    ox, oy = observation["opponent_position"]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds - do, ds, rx, ry)  # prefer being ahead (smaller ds-do), then closer
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    if dx0 != 0 and dy0 != 0:
        candidates = [(dx0, dy0), (dx0, 0), (0, dy0), (dx0, -dy0), (-dx0, dy0), (0, 0)]
    else:
        candidates = [(dx0, dy0), (dx0, 0), (0, dy0), (-dx0, dy0), (dx0, -dy0), (0, 0)]

    # deterministic fallback ordering
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            if (ddx, ddy) not in candidates and not (ddx == 0 and ddy == 0):
                candidates.append((ddx, ddy))
    if (0, 0) not in candidates:
        candidates.append((0, 0))

    best_move = (0, 0)
    best_dist = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = cheb(nx, ny, tx, ty)
        if best_dist is None or d < best_dist:
            best_dist = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]