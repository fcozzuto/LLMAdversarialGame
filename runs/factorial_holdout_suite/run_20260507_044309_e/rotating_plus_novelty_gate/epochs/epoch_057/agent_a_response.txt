def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        best_key = None
        for dx, dy, nx, ny in valid:
            k = (cheb(nx, ny, tx, ty), dx, dy)
            if best_key is None or k < best_key:
                best_key = k
                best = (dx, dy)
        return [best[0], best[1]]

    best_overall_key = None
    best_move = (0, 0)

    for dx, dy, nx, ny in valid:
        # Score: prefer resources where we are closer than opponent after this move.
        best_target_key = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            diff = od - sd  # bigger is better
            # Higher-level priority: immediate pickup, then win the race, then proximity.
            immediate = 1 if (sd == 0) else 0
            # Deterministic key: primary diff, then immediate, then our distance, then lexicographic.
            key = (-immediate, -diff, sd, rx, ry)
            if best_target_key is None or key < best_target_key:
                best_target_key = key
        # Also slight penalty for moving away from closest resource to reduce dithering.
        # Compute our current closest distance as baseline for tie-breaking.
        cur_close = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
        nxt_close = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        move_key = (best_target_key, abs(nxt_close - cur_close), dx, dy)
        if best_overall_key is None or move_key < best_overall_key:
            best_overall_key = move_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]