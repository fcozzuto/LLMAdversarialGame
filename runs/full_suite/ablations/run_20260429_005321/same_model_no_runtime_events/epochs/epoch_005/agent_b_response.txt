def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))  # Chebyshev

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer resources where opponent is relatively farther; tie-break by being closer.
        key = (do - ds, -ds, do - dist(ox, oy, w - 1 - rx, h - 1 - ry), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # Drift toward center while keeping away from opponent.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = None
        best_val = None
        for dx, dy, nx, ny in legal:
            v = (dist(nx, ny, cx, cy), -dist(nx, ny, ox, oy), -dx, -dy)
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = best
    tpar = observation.get("turn_index", 0) % 2

    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        ds_new = dist(nx, ny, tx, ty)
        do = dist(ox, oy, tx, ty)
        # Score favors reducing our distance, and maintaining advantage vs opponent.
        # Small tie-breakers make it deterministic.
        adv = do - ds_new
        safety = dist(nx, ny, ox, oy)
        center = -dist(nx, ny, (w - 1) // 2, (h - 1) // 2)
        parity_tie = -((nx + ny + tpar) & 1)
        val = (adv, -ds_new, safety, center, parity_tie, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]