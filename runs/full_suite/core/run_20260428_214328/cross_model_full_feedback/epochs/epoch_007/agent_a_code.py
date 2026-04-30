def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass
    resources_list = observation.get("resources", []) or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        ax = a - c; ax = ax if ax >= 0 else -ax
        ay = b - d; ay = ay if ay >= 0 else -ay
        return ax + ay

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): 
            continue
        if (nx, ny) in obstacles: 
            continue
        if (nx, ny) == (ox, oy):
            continue
        candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    resources = []
    for r in resources_list:
        try:
            rx, ry = r[0], r[1]
            if inside(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))
        except Exception:
            pass

    if resources:
        # Deterministic: choose nearest resource; tie by coordinates.
        tx, ty = min(resources, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
        best = None
        best_key = None
        for dx, dy, nx, ny in candidates:
            d_self = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ox, oy)
            key = (d_self, -d_opp, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: maximize distance from opponent; tie deterministically.
    best = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        d_opp = man(nx, ny, ox, oy)
        key = (-d_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [best[0], best[1]]