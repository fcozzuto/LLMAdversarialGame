def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_towards(tx, ty, fx, fy):
        dx = 0 if tx == fx else (1 if tx > fx else -1)
        dy = 0 if ty == fy else (1 if ty > fy else -1)
        nx, ny = fx + dx, fy + dy
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            # try axis moves deterministically
            for adx, ady in ((dx, 0), (0, dy), (0, 0)):
                cx, cy = fx + adx, fy + ady
                if 0 <= cx < w and 0 <= cy < h and (cx, cy) not in obstacles:
                    return [adx, ady]
        return [dx, dy]

    # Prefer targets we can reach no later than opponent (ties go to larger advantage to secure).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # key: maximize "opponent delay" while ensuring we aren't slower; then closer resource
        # if we are slower, penalize heavily to encourage switch to stealable resources.
        if sd <= od:
            key = (0, (od - sd), -sd, -rx, -ry)
        else:
            key = (1, -(sd - od), -od, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    return step_towards(tx, ty, sx, sy)