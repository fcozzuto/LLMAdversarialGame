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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = (None, -10**18)
    best_tiebreak = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # score: pick a resource where we are closest compared to opponent
        score = 0
        local_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Strongly prefer resources we can reach earlier; otherwise nearest.
            adv = od - sd
            if local_best is None:
                local_best = adv
            # Weighted to avoid overfitting on a single resource.
            score += (adv * 1000) - sd
            # If we are already adjacent to something we can claim, favor a lot.
            if adv > 0 and sd <= 1:
                score += 5000
        # Secondary: keep moving toward any resource (avoid dithering).
        # Deterministic tie-break: lexicographic on move.
        if score > best[1] or (score == best[1] and (dx, dy) < best_tiebreak):
            best = ((dx, dy), score)
            best_tiebreak = (dx, dy)

    if best[0] is None:
        return [0, 0]
    return [best[0][0], best[0][1]]