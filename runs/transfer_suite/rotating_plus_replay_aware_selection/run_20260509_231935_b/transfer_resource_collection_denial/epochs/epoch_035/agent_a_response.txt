def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    res = [(p[0], p[1]) for p in resources]
    if not res:
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    res_set = set(res)

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Immediate pickup
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in res_set and (nx, ny) not in obstacles:
            return [dx, dy]

    # Evaluate moves by "grab advantage": prefer resources we can reach sooner than opponent.
    best_move = (0, 0)
    best_key = (-10**18, -10**18, 10**18)  # (adv, scorefit, -progress)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        adv_best = -10**18
        scorefit_best = -10**18
        progress_best = -10**18

        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = dist8(nx, ny, rx, ry)
            do = dist8(ox, oy, rx, ry)
            adv = (do - ds)  # positive means we are closer
            # prefer larger lead; if lead ties, prefer nearer overall; if still ties, prefer resource in direction.
            scorefit = -ds
            progress = -(dist8(nx, ny, w - 1 - ox, h - 1 - oy))  # mild steering to opponent-opposite region
            key = (adv, scorefit, progress)
            if key > (adv_best, scorefit_best, progress_best):
                adv_best, scorefit_best, progress_best = key

        # Secondary tie-break: prefer staying closer to center of remaining resources (avg position) deterministically.
        # Compute quickly using first few resources only for determinism.
        avgx = 0
        avgy = 0
        k = 0
        for i in range(min(4, len(res))):
            avgx += res[i][0]
            avgy += res[i][1]
            k += 1
        if k:
            center_dist = dist8(nx, ny, avgx // k, avgy // k)
        else:
            center_dist = 0

        move_key = (adv_best, scorefit_best, -center_dist)
        if move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]