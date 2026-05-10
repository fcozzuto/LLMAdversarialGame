def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def step_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Resource denial: try to maximize (opponent_dist - self_dist) for our next move.
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            # Engine will keep us in place; we heavily penalize moving into obstacles/out of bounds.
            nx, ny = sx, sy
            penalty = -1000
        else:
            penalty = 0

        val = penalty
        # Evaluate best resource for this move (argmax over resources of our advantage).
        best_margin_for_this = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            margin = od - sd  # positive means we are closer
            # Tie-break: slightly prefer nearer resources (faster collection).
            score = margin * 10 - sd * 0.1
            if best_margin_for_this is None or score > best_margin_for_this:
                best_margin_for_this = score

        # If we can't gain on any resource, still move to reduce opponent's best margin.
        if best_margin_for_this is None:
            continue
        val += best_margin_for_this

        # Small anti-collision: avoid stepping closer to opponent unless it increases winning margin.
        d_to_opp = dist(nx, ny, ox, oy)
        val -= max(0, 6 - d_to_opp) * 0.3

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]