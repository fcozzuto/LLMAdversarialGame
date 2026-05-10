def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    # Baseline: which resource is best for me right now
    my_best_sd = None
    my_best = None
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        if my_best_sd is None or sd < my_best_sd:
            my_best_sd = sd
            my_best = (rx, ry)

    best_move = None  # (key, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_for_move = None  # (adv, -sd, od, sd, rx, ry)
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            if sd is None:
                continue
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive if I am closer than opponent to this resource after the move
            key = (adv, -sd, od, sd, rx, ry)
            if best_for_move is None or key > best_for_move:
                best_for_move = key

        if best_for_move is None:
            continue

        # Encourage committing to my closest resource, unless doing so loses the advantage.
        rx, ry = best_for_move[4], best_for_move[5]
        commit_bonus = 0
        if my_best is not None and (rx, ry) == my_best:
            commit_bonus = 1  # small deterministic nudge

        # Secondary: if advantage ties, prefer smaller my distance to avoid "stalling"
        adv, neg_sd, od, sd = best_for_move[0], best_for_move[1], best_for_move[2], best_for_move[3]
        final_key = (adv, sd, -od, -commit_bonus, -nx, -ny, dx, dy)
        if best_move is None or final_key > best_move[0]:
            best_move = (final_key, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]