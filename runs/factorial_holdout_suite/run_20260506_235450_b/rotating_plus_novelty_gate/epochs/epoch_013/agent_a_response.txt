def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)
    res_set = set((p[0], p[1]) for p in resources)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a target where we are (eventually) closer than the opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = man(sx, sy, rx, ry)
        op_d = man(ox, oy, rx, ry)
        key = (op_d - my_d, -my_d, -op_d, -rx, -ry)
        if best_key is None or key > best_key:
            best_key, best_t = key, (rx, ry)

    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Evaluate moves: prioritize immediate resource pickup, then improving distance advantage.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = man(nx, ny, tx, ty)
        op_d = man(ox, oy, tx, ty)
        pickup = 1 if (nx, ny) in res_set else 0

        # Encourage increasing our advantage; small preference for moving closer and away from opponent.
        val = (pickup * 1000) + (op_d - my_d) * 10 - my_d
        # If not on resource, prefer moves that also avoid letting the opponent steal nearer resources.
        if pickup == 0:
            steer = 0
            for rx, ry in resources:
                if (rx, ry) == (tx, ty):
                    continue
                my2 = man(nx, ny, rx, ry)
                op2 = man(ox, oy, rx, ry)
                steer = max(steer, op2 - my2)
            val += steer * 0.2

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]