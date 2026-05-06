def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    best_move = (0, 0)
    best_key = (-10**9, 10**9, 10**9)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If no resources, drift toward center to avoid being boxed in.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = man(nx, ny, cx, cy)
                if (d, dx, dy) < (bestd, best_move[0], best_move[1]):
                    bestd = d
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Target resource we can reach sooner than opponent; otherwise block nearest "threat".
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate best attainable objective from this step.
        step_best = (-10**9, 10**9, 10**9)
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)

            # Primary: prefer resources where we are strictly closer (or equal),
            # Secondary: maximize (opponent_dist - self_dist) to gain tempo,
            # Tertiary: slightly prefer nearer absolute distance to finish.
            gap = do - ds
            closer_flag = 1 if ds <= do else 0
            key = (closer_flag, gap, -ds)  # higher gap, higher closer_flag, higher -ds means smaller ds
            # Convert to comparable lexicographic: we want max key; do by storing minimal negative
            # but keep it simple: compare with tuple using reversed signs.
            # step_best stores (neg_score_for_max, abs_dist_for_min, tie_for_min)
            step_key = (-key[0], -key[1], -key[2])
            if step_key < step_best:
                step_best = step_key

        # Global compare between candidate moves: use the selected objective and tiebreak deterministically.
        global_key = (step_best[0], step_best[1], abs(nx - ox) + abs(ny - oy), dx, dy)
        # We want smaller global_key (since step_best already inverted).
        if global_key < best_key:
            best_key = global_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]