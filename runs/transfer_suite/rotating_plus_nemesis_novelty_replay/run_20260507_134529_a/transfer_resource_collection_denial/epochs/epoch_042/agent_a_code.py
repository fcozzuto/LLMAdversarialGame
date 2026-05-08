def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        # Deterministic flee: maximize distance from opponent
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    # Pick a target to beat the opponent (or, if impossible, pick closest resource)
    best_r = None
    best_b = -10**18
    best_ds = 10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        b = do - ds
        # Strongly prefer securing (bigger advantage), then closer to self, then deterministic tie-break
        if (b > best_b) or (b == best_b and (ds < best_ds or (ds == best_ds and (rx, ry) < best_r))):
            best_b, best_ds, best_r = b, ds, (rx, ry)

    tx, ty = best_r
    # One-step lookahead: evaluate moves by resulting "security advantage" and closeness
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Encourage capturing sooner, and avoid giving opponent an even larger edge
        val = (do2 - ds2) - 0.25 * ds2
        # Small deterministic bias to reduce dithering: prefer direction that decreases distance to target
        if val == best_val:
            curd = cheb(sx, sy, tx, ty)
            nd = cheb(nx, ny, tx, ty)
            if nd < curd:
                best_move = (dx, dy)
        elif val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]