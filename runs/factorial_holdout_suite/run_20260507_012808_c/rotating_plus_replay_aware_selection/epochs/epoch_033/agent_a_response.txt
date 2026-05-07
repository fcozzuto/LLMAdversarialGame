def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def clamp_move(dx, dy):
        if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
            return [0, 0]
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return [0, 0]
        return [dx, dy]

    if not resources:
        # deterministic fallback: move to top-left corner
        tx, ty = 0, 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return clamp_move(dx, dy)

    # Precompute nearest resource distances for opponent to estimate race pressure
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbor_obst_pen(x, y):
        p = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    p += 1
        return p

    opp_best_d = None
    opp_best = None
    for rx, ry in resources:
        d = man((ox, oy), (rx, ry))
        if opp_best_d is None or d < opp_best_d:
            opp_best_d, opp_best = d, (rx, ry)

    # Evaluate one-step moves with a conservative advantage score
    best = None
    best_move = [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            move = [dx, dy]
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue

            # Find the resource we would be closest to after moving
            my_d = None
            my_target = None
            for rx, ry in resources:
                d = man((nx, ny), (rx, ry))
                if my_d is None or d < my_d:
                    my_d, my_target = d, (rx, ry)

            # Opponent pressure: how close opponent is to that same target
            tx, ty = my_target
            od = man((ox, oy), (tx, ty))

            # Prefer taking a resource that opponent is slower for, and avoid obstacles
            advantage = (od - my_d)
            # Add slight tie-break toward smaller my_d and toward opponent's best distance
            pressure = (opp_best_d - od) if opp_best_d is not None else 0

            score = (advantage * 100) + (pressure * 10) - (my_d) - neighbor_obst_pen(nx, ny)

            if best is None or score > best:
                best = score
                best_move = move

    return clamp_move(best_move[0], best_move[1])