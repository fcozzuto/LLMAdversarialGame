def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    candidates = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0), (0, 0), (1, 0),
        (-1, 1), (0, 1), (1, 1)
    ]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = abs(nx - cx) + abs(ny - cy)
                sc = -d
                if (sc, dx, dy) > best:
                    best = (sc, dx, dy)
        return [best[1], best[2]]

    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        our_min = 10**9
        best_diff = -10**9
        for rx, ry in resources:
            our_d = abs(nx - rx) + abs(ny - ry)
            if our_d < our_min:
                our_min = our_d
            if opp_exists:
                opp_d = abs(ox - rx) + abs(oy - ry)
                diff = opp_d - our_d  # positive => we're closer (deny when negative)
                if diff > best_diff:
                    best_diff = diff

        if opp_exists:
            sc = 2.2 * best_diff - 0.15 * our_min
        else:
            sc = -our_min

        if sc > best_score or (sc == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = sc
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]