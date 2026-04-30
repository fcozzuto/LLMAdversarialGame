def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def pick_target():
        if not resources:
            return None
        best_ahead = None
        best_ahead_key = None
        best_any = None
        best_any_key = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            ahead = od - sd  # positive if we are closer
            key_a = (ahead, -sd, -od, rx, ry)
            if best_ahead_key is None or key_a > best_ahead_key:
                best_ahead_key = key_a
                best_ahead = (rx, ry)
            key_any = (-sd, -od, rx, ry)
            if best_any_key is None or key_any > best_any_key:
                best_any_key = key_any
                best_any = (rx, ry)
        rx, ry = best_ahead
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if od - sd > 0:
            return (rx, ry)
        return best_any

    target = pick_target()

    if target is None:
        # Drift toward resource-free central band; avoid moving into obstacles.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestk = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not cell_free(nx, ny):
                continue
            k = (-abs(nx - cx) - abs(ny - cy), -man(nx, ny, ox, oy), dx, dy)
            if bestk is None or k > bestk:
                bestk = k
                best = (dx, dy)
        return [best[0], best[1]]

    rx, ry = target
    initial_dist = man(sx, sy, rx, ry)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_free(nx, ny):
            continue
        sd2 = man(nx, ny, rx, ry)
        od2 = man(ox, oy, rx, ry)
        # Strongly race on distance; also reward denying by moving closer to target where opponent would also go.
        # Add a small tie-break that prefers not increasing our distance and prefers moving away from opponent.
        improves = initial_dist - sd2
        capture_bonus = 500 if (nx, ny) == (rx, ry) else 0
        score = (od2 - sd2) * 200 + improves * 20 + capture_bonus
        score += (man(nx, ny, ox, oy) - man(sx, sy, ox, oy)) * 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]