def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    best_move = [0, 0]
    best_eval = None

    # Break ties deterministically by preferring earlier deltas order.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            if nx == sx and ny == sy:
                pass
        if dx == 0 and dy == 0 and (sx, sy) in obstacles:
            return [0, 0]

        # Evaluate best resource we could target after making this move.
        # Prefer resources where we are closer than opponent (large opp_d - self_d).
        eval_best_for_move = None
        for rx, ry in resources:
            if not ok(rx, ry):
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            margin = od - sd  # positive means we arrive earlier
            # If margins tie, prefer shorter self distance; then lexicographic on resource.
            key = (margin, -sd, rx, ry)
            if eval_best_for_move is None or key > eval_best_for_move:
                eval_best_for_move = key

        if eval_best_for_move is None:
            eval_best_for_move = (-10**9, 0, 0, 0)

        if best_eval is None or eval_best_for_move > best_eval:
            best_eval = eval_best_for_move
            best_move = [nx - sx, ny - sy]

    return [int(best_move[0]), int(best_move[1])]