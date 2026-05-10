def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = observation.get("self_role", "pursuer").lower()

    cands = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    step_to_opp = (0 if ox == sx else (1 if ox > sx else -1), 0 if oy == sy else (1 if oy > sy else -1))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def clearance(nx, ny):
        if not obs_set:
            return 3
        # farther from obstacles is better; cap to keep weights stable
        d = min(abs(nx - ax) + abs(ny - ay) for (ax, ay) in obs_set)
        return d if d < 6 else 6

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    best_corner_score = max(man(sx, sy, cx, cy) for cx, cy in corners)

    # For pursuer: minimize distance and move "toward" opponent; for evader: maximize distance and move "away"
    target_sign = 1 if role == "pursuer" else -1
    best_move = [0, 0]
    best_key = None

    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        nd = man(nx, ny, ox, oy)
        align = dx * step_to_opp[0] + dy * step_to_opp[1]  # toward opponent
        away = -align
        cc = clearance(nx, ny)

        # Corner bias to break ties: evader prefers staying near farthest corner direction, pursuer opposite.
        corner_bias = max(man(nx, ny, cx, cy) for cx, cy in corners)
        corner_term = corner_bias - best_corner_score

        if target_sign == 1:
            key = (nd, -align, -cc, -corner_term)
        else:
            key = (-nd, -away, -cc, corner_term)

        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move