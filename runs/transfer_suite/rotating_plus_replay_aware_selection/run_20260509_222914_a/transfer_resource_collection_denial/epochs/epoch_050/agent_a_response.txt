def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def manh(a, b, c, d):
        da = a - c
        if da < 0:
            da = -da
        db = b - d
        if db < 0:
            db = -db
        return da + db

    tx_best, ty_best = resources[0]
    best_margin = None
    best_time = None
    for tx, ty in resources:
        ds = manh(x, y, tx, ty)
        do = manh(ox, oy, tx, ty)
        margin = do - ds
        if best_margin is None or margin > best_margin or (margin == best_margin and ds < best_time):
            best_margin = margin
            best_time = ds
            tx_best, ty_best = tx, ty

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_ds_after = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue
        ds_after = manh(nx, ny, tx_best, ty_best)
        do_now = manh(ox, oy, tx_best, ty_best)
        score = do_now - ds_after
        if best is None or score > best or (score == best and ds_after < best_ds_after):
            best = score
            best_ds_after = ds_after
            best_dx, best_dy = dx, dy

    if best is None:
        return [0, 0]
    return [int(best_dx), int(best_dy)]