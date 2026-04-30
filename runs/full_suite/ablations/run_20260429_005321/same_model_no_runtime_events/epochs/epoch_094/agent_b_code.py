def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [w - 1, h - 1]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**18)

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            my_best = -10**18
            for rx, ry in resources:
                myd = abs(nx - rx) + abs(ny - ry)
                opd = abs(ox - rx) + abs(oy - ry)
                my_best = max(my_best, (opd - myd) - 0.001 * myd)
            score = my_best
            if score > best[1]:
                best = ([dx, dy], score)
    else:
        # No visible resources: drift toward center while keeping distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dd_op = abs(nx - ox) + abs(ny - oy)
            dd_c = abs(nx - cx) + abs(ny - cy)
            score = 0.01 * dd_op - dd_c
            if score > best[1]:
                best = ([dx, dy], score)

    return best[0] if best[0] is not None else [0, 0]