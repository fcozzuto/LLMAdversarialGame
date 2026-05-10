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

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_val = -10**18
    tr = observation.get("turns_remaining", 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        move_best = -10**18
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            gap = opp_d - my_d
            # Strong preference when we can move to be strictly closer; otherwise minimize our distance.
            val = gap * 100 - my_d * 3
            if my_d == 0:
                val += 1000 + tr * 0.1
            # Slightly prefer targets with closer relative advantage, even if not strictly.
            val += (gap if gap > 0 else -0.5) * 10
            if val > move_best:
                move_best = val
        if move_best > best_val:
            best_val = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]