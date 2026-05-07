def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate best resource we can "lock in" from the new position.
        local_best = None
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            lead = od - sd  # positive means we are closer than opponent after this move
            # Prefer winning contests (positive lead), then faster capture and smaller self distance.
            key = (lead, -sd, -man(ox, oy, nx, ny))
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue

        # Break ties deterministically by preferring moves with higher "immediate capture chance".
        # immediate chance approximated by whether we land on a resource.
        on_res = any((nx == rx and ny == ry) for (rx, ry) in resources)
        global_key = (local_best[0], local_best[1], int(on_res), -man(nx, ny, w - 1, h - 1))
        if best_key is None or global_key > best_key:
            best_key = global_key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]