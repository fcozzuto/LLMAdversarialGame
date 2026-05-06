def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or []) if tuple(r) and tuple(map(int, r)) not in obstacles]
    cx, cy = w // 2, h // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [dx, dy]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate by best contested resource after this move
        ns = None
        for rx, ry in resources:
            sd = man((nx, ny), (rx, ry))
            od = man((ox, oy), (rx, ry))
            # Prefer resources I'm closer to; penalize where opponent is closer.
            # Tie-breaker biases toward center and away from being stuck.
            val = sd - 1.15 * od + 0.03 * (abs(nx - cx) + abs(ny - cy))
            if ns is None or val < ns:
                ns = val
        if ns is None:
            continue
        # Additional small tie-breaker: avoid moving into opponent proximity too much
        ns += 0.01 * man((nx, ny), (ox, oy))
        if best_score is None or ns < best_score:
            best_score = ns
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]