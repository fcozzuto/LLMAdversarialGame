def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Predict opponent's next target as its nearest resource.
    pred = None
    pred_d = 10**9
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < pred_d or (d == pred_d and (rx, ry) < (pred[0], pred[1]) if pred else True):
            pred_d = d
            pred = (rx, ry)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18

    def step_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue

        # Evaluate by whether we can beat opponent to some resource, and especially to the predicted one.
        val = -man(nx, ny, ox, oy) * 0.01  # slight bias away from getting stuck with opponent
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            ahead = od - sd  # positive means we are closer (in manhattan)
            # Strongly prioritize contesting predicted target.
            contest = 2000 if pred == (rx, ry) else 0
            val_here = ahead * 100 - sd + contest
            # If we tie, prefer the predicted target; otherwise prefer larger ahead.
            if ahead == 0 and pred == (rx, ry):
                val_here += 50
            val = max(val, val_here)

        # Deterministic tie-break: prefer lexicographically smallest (dx,dy) among equals.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]