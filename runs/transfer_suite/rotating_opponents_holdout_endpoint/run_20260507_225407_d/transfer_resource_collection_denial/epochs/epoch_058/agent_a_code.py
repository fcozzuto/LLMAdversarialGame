def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def step_toward(tx, ty):
        deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best_m = (0, 0)
        best_k = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            adv_new = od - sd  # positive means we're closer
            k = (-adv_new, sd, man(ox, oy, nx, ny))
            if best_k is None or k < best_k:
                best_k = k
                best_m = (dx, dy)
        return [best_m[0], best_m[1]]

    # Choose resource: maximize advantage (opponent distance - self distance), then shorter self distance
    best = None
    best_k = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not valid(tx, ty):
            continue
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        adv = od - sd
        k = (-adv, sd, od, tx, ty)
        if best_k is None or k < best_k:
            best_k = k
            best = (tx, ty)

    if best is not None:
        return step_toward(best[0], best[1])

    # No resources: drift toward center while avoiding obstacles
    cx, cy = (w - 1) // 2, (h - 1) // 2
    return step_toward(cx, cy)