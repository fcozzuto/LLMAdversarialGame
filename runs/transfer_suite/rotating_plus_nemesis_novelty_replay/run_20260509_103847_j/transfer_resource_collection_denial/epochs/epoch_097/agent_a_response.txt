def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_key = None
    best_move = (0, 0)

    # Deterministic: evaluate all moves by "immediate advantage" against best reachable resource.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_nearest = 10**9
        opp_nearest = 10**9
        best_adv = -10**9
        best_res = None

        for rx, ry in resources:
            d_my = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            if d_my < my_nearest:
                my_nearest = d_my
            if d_op < opp_nearest:
                opp_nearest = d_op
            adv = d_op - d_my  # higher => we are closer than opponent
            if adv > best_adv or (adv == best_adv and (rx, ry) < best_res):
                best_adv = adv
                best_res = (rx, ry)

        # Also bias toward occupying opponent's row/column when it doesn't hurt advantage too much.
        row_bias = 1 if best_res and best_res[1] == oy else 0
        col_bias = 1 if best_res and best_res[0] == ox else 0

        # Prevent being lured into poor targets: penalize moving away from overall nearest resource.
        my_dist_now = man(sx, sy, best_res[0], best_res[1]) if best_res else 0
        progress = my_dist_now - my_nearest  # positive if improved

        # Opponent threat: if they are very close to any resource, prefer moves that increase our advantage.
        opp_pressure = 1 if opp_nearest <= 2 else 0

        key = (
            -best_adv,                 # maximize advantage
            -progress,                 # maximize immediate progress to our chosen resource
            -(row_bias + col_bias),    # small deterministic bias
            my_nearest,                # then closest to some resource
            opp_nearest,               # then deny proximity to resources
            nx, ny, dx, dy             # deterministic tie-break
        )

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]