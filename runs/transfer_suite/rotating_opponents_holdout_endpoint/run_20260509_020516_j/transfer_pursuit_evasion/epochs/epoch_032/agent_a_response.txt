def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        if it is None:
            continue
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        a, b = abs(x1 - x2), abs(y1 - y2)
        return a if a >= b else b

    # If role ambiguous, fall back to "evader": maximize distance.
    score_sign = -1 if i_am_pursuer else 1

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, ox, oy)
        # Avoid stepping near obstacles (helps with tight cornering)
        near_pen = 0
        for (bx, by) in obstacles:
            dist = cheb(nx, ny, bx, by)
            if dist == 1:
                near_pen += 5
            elif dist == 0:
                near_pen += 50
        # Also avoid moving into a "mirror" where opponent can immediately align better
        align = cheb(ox, oy, nx, ny)
        val = score_sign * d - near_pen - 0.1 * align
        # Deterministic tie-break: prefer lower |dx|+|dy| then lexicographic move
        key = (val, -abs(dx) - abs(dy), -dx, -dy)
        if best is None or key > best_val:
            best_val = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]