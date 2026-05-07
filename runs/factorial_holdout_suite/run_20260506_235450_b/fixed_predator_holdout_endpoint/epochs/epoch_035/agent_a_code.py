def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    res_set = set((p[0], p[1]) for p in resources)

    def nearest_dist(px, py):
        best = None
        for rx, ry in resources:
            d = man(px, py, rx, ry)
            if best is None or d < best:
                best = d
        return best if best is not None else 10**9

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_score = None
    self_near = nearest_dist(sx, sy)
    opp_near = nearest_dist(ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        self_d = nearest_dist(nx, ny)
        opp_d = opp_near  # opponent position unchanged this turn
        grab = 1 if (nx, ny) in res_set else 0

        # Main goal: keep advantage over opponent, but also improve our progress.
        # When grabs are possible, strongly prioritize them.
        score = (grab * 10**6) + (opp_d - self_d) * 1000 - self_d
        # Small deterministic tie-break: prefer staying closer to current self_near progress.
        score += -abs(self_d - self_near)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all moves blocked (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]