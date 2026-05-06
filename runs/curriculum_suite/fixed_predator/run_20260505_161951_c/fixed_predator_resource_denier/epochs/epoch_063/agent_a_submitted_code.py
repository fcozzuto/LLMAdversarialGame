def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles", [])
    obs = set(obstacles if all(isinstance(p, (list, tuple)) and len(p) == 2 for p in obstacles) else [])
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    resources = observation.get("resources", []) or []
    oppd = dist(x, y, ox, oy)
    if resources:
        tx, ty = min(resources, key=lambda p: dist(x, y, p[0], p[1]))
        best = None
        bestv = None
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            td = dist(nx, ny, tx, ty)
            od = dist(nx, ny, ox, oy)
            v = (-td, -od, dx, dy)  # minimize target distance, maximize opponent distance
            if bestv is None or v < bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]

    # No resources: maximize distance from opponent (tie-break by center-ish)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        od = dist(nx, ny, ox, oy)
        cdist = abs(nx - cx) + abs(ny - cy)
        v = (-od, cdist, dx, dy)  # maximize opponent distance, then closer to center
        if bestv is None or v < bestv:
            bestv, best = v, [dx, dy]
    return best if best is not None else [0, 0]