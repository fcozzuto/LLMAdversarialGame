def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obs_penalty(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    # Move scoring:
    # For each resource, prefer states where we are closer than opponent (opp_d - self_d large),
    # while breaking ties by actually getting closer to the resource.
    # Also penalize obstacle proximity and drifting away from the current best.
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)

        # Disallow stepping onto obstacles if possible (engine may keep in place anyway)
        if (nx, ny) in obstacles:
            continue

        best_for_move = None  # (primary, secondary)
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            primary = od - sd
            secondary = -sd
            val = (primary, secondary)
            if best_for_move is None or val > best_for_move:
                best_for_move = val

        if best_for_move is None:
            continue

        primary, secondary = best_for_move
        score = (primary, secondary - 0.15 * obs_penalty(nx, ny))

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]