def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy
        d_inf = d2 if d2 > 0 else 0

        # Mobility: prefer moves with more options (avoid cornering ourselves).
        mob = 0
        for a, b in dirs:
            x2, y2 = nx + a, ny + b
            if ok(x2, y2):
                mob += 1

        # Obstacle-aware wall bias: push toward center when evading, toward capture line when pursuing.
        center_bias = -((nx - (w - 1) / 2) ** 2 + (ny - (h - 1) / 2) ** 2)

        if evader:
            # Maximize distance, then maximize mobility, then center.
            key = (d2, mob, center_bias)
        else:
            # Minimize distance; add tie-breakers to keep pressure (alignment toward opponent).
            # Alignment prefers moving such that our displacement matches opponent displacement in x/y signs.
            sdx = 0 if ox == sx else (1 if ox > sx else -1)
            sdy = 0 if oy == sy else (1 if oy > sy else -1)
            ax = nx - sx
            ay = ny - sy
            align = (ax == sdx) + (ay == sdy)
            key = (-d2, align, mob, center_bias)

        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]