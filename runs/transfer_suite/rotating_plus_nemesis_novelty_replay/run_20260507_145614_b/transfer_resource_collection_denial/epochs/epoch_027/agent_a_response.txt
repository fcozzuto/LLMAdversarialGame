def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    center_x, center_y = (w - 1) // 2, (h - 1) // 2

    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        # Intercept sweep_rows: prioritize resources on opponent's current row (then adjacent rows).
        local_best = -10**18
        for rx, ry in resources:
            if not valid(rx, ry):
                continue
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            row_bonus = 40 if ry == oy else (18 if abs(ry - oy) == 1 else 0)
            # Prefer stealing/contesting: higher when opponent is closer than we are (or when close anyway).
            contend = (opp_d - self_d) * 0.7
            # Prefer being near targets and slightly toward center for tie breaks.
            center_bias = -(abs(nx - center_x) + abs(ny - center_y)) * 0.02
            val = row_bonus + contend - self_d + center_bias
            if val > local_best:
                local_best = val

        if local_best > best_val:
            best_val = local_best
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]