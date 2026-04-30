def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))  # Chebyshev

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    avail_resources = [(rx, ry) for (rx, ry) in resources if (rx, ry) not in obstacles]
    if not avail_resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_key = None
        for dx, dy, nx, ny in legal:
            key = (-dist(nx, ny, cx, cy), dist(nx, ny, ox, oy))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    best_overall = None
    best_overall_key = None
    for rx, ry in avail_resources:
        self_d = dist(sx, sy, rx, ry)
        opp_d = dist(ox, oy, rx, ry)
        # Target resources we can reach as good or better than opponent.
        key = (opp_d - self_d, -self_d, rx, ry)
        if best_overall_key is None or key > best_overall_key:
            best_overall_key = key
            best_overall = (rx, ry)

    tx, ty = best_overall
    best_move = None
    best_key = None
    for dx, dy, nx, ny in legal:
        # Evaluate the strongest "winning" target from this move.
        local_best = None
        local_key = None
        for rx, ry in avail_resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            key = (od - sd, -sd, -dist(ox, oy, nx, ny))
            if local_key is None or key > local_key:
                local_key = key
                local_best = (rx, ry)
        # Encourage moving toward our chosen target (prevents dithering).
        toward = -dist(nx, ny, tx, ty)
        # Secondary: reduce distance to chosen target while keeping competitive advantage.
        key = (local_key[0], local_key[1], toward, -dist(nx, ny, ox, oy), local_best[0], local_best[1])
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move else [0, 0]