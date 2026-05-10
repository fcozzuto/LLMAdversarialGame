def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None  # (score_tuple, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate best resource choice from this next position.
        best_for_move = None
        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            net = opp_d - self_d  # positive means we are closer than opponent
            # Strongly discourage moves where we are behind.
            if self_d > opp_d:
                net -= 4 * (self_d - opp_d)
            # Prefer nearer even if net ties, and avoid very long chases.
            cand = (net, -self_d)
            if best_for_move is None or cand > best_for_move:
                best_for_move = cand
        if best_for_move is None:
            continue
        if best is None or best_for_move > best[0]:
            best = (best_for_move, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]