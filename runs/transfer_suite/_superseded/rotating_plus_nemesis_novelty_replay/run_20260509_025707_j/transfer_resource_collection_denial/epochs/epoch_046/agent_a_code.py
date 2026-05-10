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

    turns_remaining = observation.get("turns_remaining", 0) or 0

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_val = None  # tuple compare

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        move_best = None  # (priority, -sd, -od, sd, od, rx, ry)
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue

            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Prefer resources we can beat, then those that keep opponent farther away.
            # Turns remaining: slight bias toward closer resources early.
            beat_margin = od - sd
            if sd == 0:
                pr = 10**6
            else:
                pr = beat_margin * 1000 - sd

                # Encourage taking a resource if it is reachable and likely contested.
                if turns_remaining > 0 and sd <= turns_remaining:
                    pr += 50
                if turns_remaining > 0 and od <= turns_remaining and beat_margin <= 0:
                    pr -= 25

            # Higher pr better; tie-break by minimizing our distance, then maximizing opponent distance.
            cand = (pr, -sd, od, sd, od, rx, ry)
            if move_best is None or cand > move_best:
                move_best = cand

        if move_best is None:
            continue

        # Also discourage moves that reduce our best winning margin for the top resource.
        # Compare using the pr part plus our own distance to that chosen resource.
        pr, negsd, od, sd, _, _, _ = move_best
        val = (pr, negsd, od, -abs(dx) - abs(dy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]