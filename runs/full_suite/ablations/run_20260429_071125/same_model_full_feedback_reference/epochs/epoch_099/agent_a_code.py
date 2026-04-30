def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick resource that gives the best current relative position (favor being closer than opponent)
    if resources:
        best_r = resources[0]
        best_margin = -10**9
        for (rx, ry) in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            margin = do - ds  # positive means we are closer
            # tie-break: nearer overall, then consistent ordering
            key = (margin, -(ds + 0.01 * rx))
            bkey = (best_margin, - (man(sx, sy, best_r[0], best_r[1]) + 0.01 * best_r[0]))
            if key > bkey:
                best_margin = margin
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        d_to_t_opp = man(ox, oy, tx, ty)
        ds_now = man(sx, sy, tx, ty)
        # Value: get closer to target, and reduce opponent's ability by improving our margin
        # Also keep distance from opponent to avoid being "chased" (indirect).
        margin_after = d_to_t_opp - ds
        val = 100.0 * margin_after - 2.0 * ds + 0.03 * do - (0.01 * (nx + ny))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]