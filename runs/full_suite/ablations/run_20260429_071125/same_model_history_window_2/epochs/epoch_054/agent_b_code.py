def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # Select best target for self: minimize self distance, prefer where opponent is farther
    best_t = resources[0]
    best_key = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # key: smaller ds, larger (do-ds), then deterministic tie by coords
        key = (ds, -(do - ds), tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    # If opponent is threatening a resource closer than us and it's near, intercept/block
    intercept_t = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        if do + 1 < ds and do <= 2:  # opponent much closer and already in range
            if intercept_t is None:
                intercept_t = (tx, ty)
            else:
                # choose the most urgent: smallest do, then deterministic
                if cheb(ox, oy, tx, ty) < cheb(ox, oy, intercept_t[0], intercept_t[1]):
                    intercept_t = (tx, ty)
                elif cheb(ox, oy, tx, ty) == cheb(ox, oy, intercept_t[0], intercept_t[1]) and (tx, ty) < intercept_t:
                    intercept_t = (tx, ty)

    target = intercept_t if intercept_t is not None else best_t
    tx, ty = target

    # Choose move minimizing distance to target; secondary: maximize distance to opponent (defensive)
    best = (0, 0, sx, sy)
    best_val = None
    for dx, dy, nx, ny in valid:
        dist = cheb(nx, ny, tx, ty)
        opp_dist = cheb(nx, ny, ox, oy)
        # prefer smaller dist, then larger opp_dist, then deterministic by dx,dy order implicitly via dirs
        val = (dist, -opp_dist, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy, nx, ny)

    return [best[0], best[1]]