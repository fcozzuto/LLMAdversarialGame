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

    if not resources:
        return [0, 0]

    # Target selection: prefer resources where we are closer than opponent; break ties by closer distance and farther-from-opponent on "contested" ones.
    best_target = None
    best_key = None
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer
        # Key: maximize adv; then minimize sd; then maximize od (prefer stealing/controlling)
        key = (-(adv), sd, -(od))
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry, sd, od, adv)

    rx, ry, sd0, od0, adv0 = best_target

    # If heavily contested (opponent significantly closer), switch to best "safety" target where our advantage is less negative but still best overall.
    if adv0 < -2:
        best_alt = None
        best_key = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            ax, ay = r[0], r[1]
            if (ax, ay) in obstacles:
                continue
            sd = man(sx, sy, ax, ay)
            od = man(ox, oy, ax, ay)
            adv = od - sd
            # Here we prefer least-bad contest: maximize adv but avoid super-far targets
            key = (-(adv), sd)
            if best_key is None or key < best_key:
                best_key = key
                best_alt = (ax, ay, sd, od, adv)
        rx, ry, sd0, od0, adv0 = best_alt

    # Move scoring: choose adjacent cell that improves our distance to the chosen target,
    # and secondarily reduces opponent distance to that same target if it is not hopeless.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)
        # Encourage capturing quickly; discourage giving opponent an even faster line by moving away from target.
        score = (sd, abs(sd - od), -adv0)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]