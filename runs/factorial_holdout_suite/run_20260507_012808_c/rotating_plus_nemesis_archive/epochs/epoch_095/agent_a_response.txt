def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    if (sx, sy) in resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        for dx, dy in [(1, 0), (0, 1), (1, 1), (0, 0), (1, -1), (-1, 0), (0, -1), (-1, 1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in resources:
        sd = man((sx, sy), (tx, ty))
        od = man((ox, oy), (tx, ty))
        # Race advantage first; tie-break toward faster self.
        key = (od - sd, -sd, -abs(tx - ox) - abs(ty - oy), tx, ty)
        if best_key is None or key > best_key:
            best_key, best = key, (tx, ty)

    tx, ty = best
    desired = (0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1))

    def step_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = None
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        # Prefer moves that reduce distance to target and keep winning the race.
        sd2 = man((nx, ny), (tx, ty))
        od2 = man((ox, oy), (tx, ty))
        # Small penalty for moving away diagonally vs axis-aligned tie.
        diag_pen = 1 if (dx != 0 and dy != 0) else 0
        key = (od2 - sd2, -sd2, -diag_pen, dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key, best_move = key, (dx, dy)

    if best_move is None:
        return [0, 0]
    # If desired step exists, bias to it deterministically.
    if step_ok(sx + desired[0], sy + desired[1]):
        return [desired[0], desired[1]]
    return [best_move[0], best_move[1]]