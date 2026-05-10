def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx = min(w - 1, max(0, w // 2))
        ty = min(h - 1, max(0, h // 2))
        best = (0, 0, 10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < best[2]:
                best = (dx, dy, d)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_score = -10**18

    # Deterministic preference weights:
    # 1) maximize advantage in reaching a resource first (opponent path length - ours)
    # 2) break ties by shorter own distance (faster collection)
    # 3) slight preference to deny (also consider making opponent farther from that resource)
    # 4) late-game: prefer closer resources
    late_factor = 1.0
    if turns_remaining is not None:
        # Smaller turns_remaining -> more greedy
        late_factor = 0.6 + 0.4 * (min(64, max(0, turns_remaining)) / 64.0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        move_score = -10**18
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue

            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # If we are substantially behind, deprioritize.
            adv = od - sd  # positive means we can reach sooner/equal
            if adv < -2 and late_factor < 0.9:
                continue

            # Score: advantage dominates, then speed; add denial term.
            # Denial term: make opponent distance larger for the chosen target.
            score = (adv * 1000) + (-sd * 10 * late_factor) + (od * -0.02) + (-abs(sd - od) * 0.1)

            # Extra deterministic tie-break: prefer resources with "smaller" coordinates
            score += -(rx * 0.001 + ry * 0.0005)

            if score > move_score:
                move_score = score

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]