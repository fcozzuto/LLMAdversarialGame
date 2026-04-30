def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick target resource that we can reach earlier than opponent (tie-broken by being closer to us).
    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Higher key is better: more advantage in reaching first.
            key = (do - ds, -ds, -abs(rx - ox) - abs(ry - oy))
            if best_key is None or key > best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # No known resources: pressure opponent side to deny future.
        tx, ty = ox, oy

    # Avoid obstacles by selecting feasible move maximizing closeness to target,
    # with a secondary preference for increasing distance from opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        dself = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target. Secondary: don't get too close to opponent.
        val = (-dself, dop, -cheb(sx, sy, tx, ty))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]