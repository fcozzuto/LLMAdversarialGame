def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("hunt" in role) or ("chaser" in role) or ("seeker" in role) or ("hunter" in role)

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def obs_pen4(x, y):
        pen = 0
        if (x + 1, y) in obstacles: pen += 1
        if (x - 1, y) in obstacles: pen += 1
        if (x, y + 1) in obstacles: pen += 1
        if (x, y - 1) in obstacles: pen += 1
        return pen

    def center_bias(x, y):
        dx, dy = x - cx, y - cy
        return dx * dx + dy * dy

    best = None
    bestv = None

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        p = obs_pen4(nx, ny)
        cb = center_bias(nx, ny)
        # Pursuer: approach + avoid being boxed. Evader: increase distance + seek safer spacing.
        if is_pursuer:
            v = d + 5.0 * p + 0.02 * cb
        else:
            v = (-d) + 6.0 * p - 0.02 * cb
        if best is None or v < bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]