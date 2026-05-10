def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    if not resources:
        return [0, 0]

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate the best resource we can take after this move.
        # Primary: maximize (op_dist - my_dist) -> take resources sooner than opponent.
        # Secondary: closer resources / fewer steps. Tertiary: prefer earlier coordinates deterministically.
        local_best = None
        for rx, ry in res_list:
            my_d = dist(nx, ny, rx, ry)
            op_d = dist(ox, oy, rx, ry)
            diff = op_d - my_d
            on_res = 1.0 if (nx, ny) == (rx, ry) else 0.0
            # Encourage immediate pickup and winning races.
            score = (diff * 10.0) + on_res * 100.0 + (-my_d * 1.0)
            tie = (-rx, -ry)  # deterministic
            key = (score, tie)
            if local_best is None or key > local_best:
                local_best = key

        # If we can stand on any resource, that move should dominate naturally via score.
        if local_best is None:
            continue

        if best is None or local_best > best:
            best = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]