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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)
    def around_blocked(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    c += 1
        return c

    if not resources:
        return [0, 0]

    tr = observation.get("turns_remaining", 0)
    near_end = 1 if tr <= 6 else 0

    best_move = (None, -10**9, 0, 0)  # dx, score, sd, od
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        chosen = None
        best_for = (-10**9, None, None)  # score, sd, od
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd == 0 and od != 0:
                adv = 10**6
            else:
                adv = od - sd
            block = around_blocked(rx, ry)
            # Prefer resources closer than opponent; near end prefer absolute proximity.
            score = adv * 1000 - sd * (10 + near_end * 60) + block * (-2)
            # Deterministic tie-break: favor lower sd then lexicographic target.
            if (score, -sd, -od, rx, ry) > (best_for[0], -best_for[1] if best_for[1] is not None else 0, -best_for[2] if best_for[2] is not None else 0, -10**9, -10**9):
                best_for = (score, sd, od)
                chosen = (rx, ry)
        if chosen is None:
            continue
        score, sd, od = best_for
        if (score, -sd, od, dx, dy) > (best_move[1], -best_move[2], best_move[3], -10**9, -10**9):
            best_move = ( (dx, dy), score, sd, od )

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]