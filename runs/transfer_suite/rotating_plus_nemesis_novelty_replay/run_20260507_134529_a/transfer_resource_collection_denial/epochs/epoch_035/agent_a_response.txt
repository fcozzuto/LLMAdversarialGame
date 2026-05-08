def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # If no resources, just hold (or lightly drift toward center to avoid useless contest).
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx = 0 if sx == cx else (1 if cx > sx else -1)
        ty = 0 if sy == cy else (1 if cy > sy else -1)
        nx, ny = sx + tx, sy + ty
        if free(nx, ny):
            return [tx, ty]
        return [0, 0]

    # Pick a target resource by maximizing contest advantage; break ties by proximity and lower x/y.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # higher => we are closer (or opponent further)
        # Prefer closer absolute ds after adv; deterministic tie-break.
        key = (adv, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    # Move one step toward target with greedy step minimizing our distance; consider validity.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        # Use contest as primary; then ensure we actually progress.
        val = (do2 - ds2, -ds2, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]