def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def step_toward(tx, ty, x, y):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        # try diagonal/combined first
        if legal(x + dx, y + dy):
            return [dx, dy]
        # then axis options deterministically
        nx, ny = x + dx, y
        if legal(nx, ny):
            return [dx, 0]
        nx, ny = x, y + dy
        if legal(nx, ny):
            return [0, dy]
        # blocked: deterministic small search among 9 moves around self
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = x + ddx, y + ddy
                if legal(nx, ny):
                    return [ddx, ddy]
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        return step_toward(tx, ty, sx, sy)

    # Prefer resources we can reach earlier than opponent (maximize opp_dist - self_dist).
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        # tie-break deterministically with distance to center and coordinates
        cx, cy = w / 2, h / 2
        center_bias = abs(rx - cx) + abs(ry - cy)
        key = (-lead, ds, center_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    return step_toward(tx, ty, sx, sy)