def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not ok(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    if not resources:
        # If no resources, stay or drift toward center-ish deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                key = (dist(nx, ny, cx, cy), dx == 0 and dy == 0, dx, dy)
                if best is None or key < best[0]:
                    best = (key, dx, dy)
        return [int(best[1]), int(best[2])] if best else [0, 0]

    # Choose the best target resource based on our advantage
    best_r = None
    best_adv = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # higher advantage if we are closer; tie-break deterministically
        adv_key = (-(ds - do), ds, rx, ry)
        if best_adv is None or adv_key < best_adv:
            best_adv = adv_key
            best_r = (rx, ry)
    rx, ry = best_r

    # Evaluate each legal move by (1) our distance to target, (2) opponent distance to target after move,
    # and (3) small tie-break toward decreasing our distance to target.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds2 = dist(nx, ny, rx, ry)
        do2 = dist(ox, oy, rx, ry)
        key = (ds2, (ds2 - do2), (abs(dx) + abs(dy)), dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])] if best else [0, 0]