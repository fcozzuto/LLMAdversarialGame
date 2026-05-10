def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
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

    # Prefer a move that wins (or ties) distance to a resource; otherwise moves closer.
    best = None  # (win_adv, self_dist, opp_dist, -resource_count_nearby, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_for_move = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue

            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # win_adv positive means we are closer than opponent
            win_adv = od - sd

            # extra tie-break: prefer resources that are also close to current self position
            sp = man(sx, sy, rx, ry)
            # crowding: number of resources near target (helps deterministic tie-break)
            crowd = 0
            for rr in resources:
                if rr is None or len(rr) < 2:
                    continue
                tx, ty = rr[0], rr[1]
                if (tx, ty) in obstacles:
                    continue
                if man(rx, ry, tx, ty) <= 2:
                    crowd += 1

            key = (win_adv, -sd, od, sp, crowd)
            if best_for_move is None or key > best_for_move:
                best_for_move = key

        if best_for_move is None:
            continue

        # Key corresponds to best_for_move; unpack components for overall move selection.
        win_adv, neg_sd, od, sp, crowd = best_for_move
        self_dist = -neg_sd
        move_key = (win_adv, self_dist, od, -crowd, dx, dy)
        if best is None or move_key > best:
            best = move_key

    if best is None:
        return [0, 0]
    return [best[-2], best[-1]]