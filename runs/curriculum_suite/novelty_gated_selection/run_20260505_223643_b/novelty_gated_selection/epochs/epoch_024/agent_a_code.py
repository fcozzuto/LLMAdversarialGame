def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (do - ds, -ds, rx, ry)  # prefer we are closer than opponent; then smaller ds
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    sx1, sy1 = sx, sy
    if sx1 < 0: sx1 = 0
    elif sx1 >= w: sx1 = w - 1
    if sy1 < 0: sy1 = 0
    elif sy1 >= h: sy1 = h - 1

    stepx = 0 if tx == sx1 else (1 if tx > sx1 else -1)
    stepy = 0 if ty == sy1 else (1 if ty > sy1 else -1)

    candidates = []
    candidates.append((stepx, 0))
    candidates.append((0, stepy))
    if stepx != 0 and stepy != 0:
        if abs(tx - (sx1 + stepx)) + abs(ty - sy1) <= abs(tx - sx1) + abs(ty - (sy1 + stepy)):
            candidates.append((stepx, 0))
        else:
            candidates.append((0, stepy))
    candidates.append((0, 0))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_score = -10**18
    curd = man(sx1, sy1, tx, ty)
    for dx, dy in candidates:
        nx, ny = sx1 + dx, sy1 + dy
        if not valid(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        # maximize progress; slight preference to stay away from opponent if same progress
        score = (curd - nd) * 1000 - man(ox, oy, nx, ny)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]