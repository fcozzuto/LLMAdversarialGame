def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        candidates = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for tx, ty in candidates:
            v = (manh(ox, oy, tx, ty), -manh(sx, sy, tx, ty), tx, ty)
            if best is None or v > best:
                best = v
                tx_best, ty_best = tx, ty
        dx = 0 if tx_best == sx else (1 if tx_best > sx else -1)
        dy = 0 if ty_best == sy else (1 if ty_best > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        if valid(sx + dx, sy):
            return [dx, 0]
        if valid(sx, sy + dy):
            return [0, dy]
        # fallback
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Preselect target resource by global heuristic
    best_res = None
    for rx, ry in resources:
        sdist = manh(sx, sy, rx, ry)
        odist = manh(ox, oy, rx, ry)
        v = (odist - sdist, -sdist, -rx, -ry)  # deterministic tie-break
        if best_res is None or v > best_res:
            best_res = v
            tx, ty = rx, ry

    # Choose move that best improves relative approach to the target (with opponent distance tie-break)
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s2 = manh(nx, ny, tx, ty)
        o2 = manh(ox, oy, tx, ty)
        # If target is blocked away, also consider being closer to any resource
        any_best = 10**9
        for rx, ry in resources:
            any_best = min(any_best, manh(nx, ny, rx, ry))
        v = (o2 - s2, -s2, -any_best, dx, dy)
        if best_move is None or v > best_move:
            best_move = v
            bd = (dx, dy)
    if best_move is not None:
        return [bd[0], bd[1]]

    # Fallback: any valid move
    for dx, dy in moves:
        if valid(sx + dx, sy + dy):
            return [dx, dy]
    return [0, 0]