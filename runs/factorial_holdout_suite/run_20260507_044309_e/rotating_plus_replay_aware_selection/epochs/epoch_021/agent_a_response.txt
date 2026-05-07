def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    cx, cy = w // 2, h // 2
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = cx, cy
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            center = cheb(rx, ry, cx, cy)
            # If we can beat opponent on arrival, prioritize that strongly; else avoid giving them easy grabs.
            key = (-adv, ds, center) if adv >= 0 else (10 + adv, ds, center)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best if best is not None else (cx, cy)
    best_move = (0, 0)
    best_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Deterministic tie-break: lower dist, then closer to center, then lexicographic move
        cen = cheb(nx, ny, cx, cy)
        key = (d, cen, dx, dy)
        if best_dist is None or key < best_dist:
            best_dist = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]