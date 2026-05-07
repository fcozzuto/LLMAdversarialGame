def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res_set = set(tuple(r) for r in resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2; ax = -ax if ax < 0 else ax
        ay = y1 - y2; ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d_min = 10**9
        margin_best = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            my_d_min = myd if myd < my_d_min else my_d_min
            m = opd - myd  # positive means we are closer than opponent to that resource
            if m > margin_best:
                margin_best = m
        # If no resources, just drift toward opponent's side (deterministic)
        if not resources:
            key = (0, abs((w-1) - nx) + abs((h-1) - ny), dx, dy)
        else:
            # Prefer making the best margin first, then shorter distance to our closest resource
            key = (-margin_best, my_d_min, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]