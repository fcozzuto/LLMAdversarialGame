def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def free(x, y):
        return inb(x, y) and (x, y) not in obs
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),  (0, 0),  (0, 1),
            (1, -1),  (1, 0),  (1, 1)]
    if resources:
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources we are not behind on; otherwise minimize behind-amount.
            lead = do - ds
            tie = -((rx * 131 + ry) % 997)
            key = (-1 if lead < 0 else 0, -lead, ds, tie)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        ds1 = man(nx, ny, tx, ty)
        do1 = man(ox, oy, tx, ty)
        # Primary: get closer; secondary: keep/take lead vs opponent; tertiary: avoid dead-center tie.
        lead1 = do1 - ds1
        center_bias = -man(nx, ny, (w - 1) // 2, (h - 1) // 2)
        key = (ds1, -lead1, -((nx * 131 + ny) % 997), -center_bias)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]