def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Choose resource that gives best "deny" margin after this step.
        # Margin > 0 means we are closer (or equal) than opponent.
        local_best = None
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            margin = do - ds
            # Prefer: high margin, then smaller ds (faster collection), then deterministic ordering.
            val = (margin, -ds, -rx, -ry)
            if local_best is None or val > local_best:
                local_best = val
        # Also slightly prefer moving toward opponent's nearest resource to disrupt denier routes.
        opp_near = min(res, key=lambda r: man(ox, oy, r[0], r[1]))
        disrupt = -man(nx, ny, opp_near[0], opp_near[1])
        total = (local_best[0], local_best[1], disrupt, -dx, -dy)
        if best_val is None or total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]