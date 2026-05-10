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

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_dxdy = (0, 0)
    best_score = -10**18

    if not resources:
        return [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # pick the best resource for this next position
        local_best = -10**18
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue

            my_sd = man(nx, ny, rx, ry)
            if my_sd < 0:
                continue
            opp_sd = man(ox, oy, rx, ry)

            # advantage: we want opp farther than us; also prefer being close now
            adv = opp_sd - my_sd
            score = adv * 12 - my_sd * 1.0
            # slight preference to avoid going past resources (tie-break deterministically)
            score += -0.001 * (rx + 3 * ry)

            if score > local_best:
                local_best = score

        if local_best > best_score:
            best_score = local_best
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]