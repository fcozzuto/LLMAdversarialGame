def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    if opp_t:
        tx, ty = min(opp_t, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = ox, oy

    self_cnt = observation.get("self_territory_count", len(self_t))
    opp_cnt = observation.get("opponent_territory_count", len(opp_t))
    aggressive = 1.0 if opp_cnt >= self_cnt else 0.6

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d = abs(nx - tx) + abs(ny - ty)
        score = -d

        if (nx, ny) in opp_t:
            score += 5000 * aggressive
        elif (nx, ny) in unclaimed:
            score += 1200
        elif (nx, ny) in self_t:
            score += 120

        # Nudge toward nearest opponent direction; reduces dithering
        score += 10 * (-(abs(nx - ox) + abs(ny - oy)))

        # Prefer not stepping away from center late-game
        tr = observation.get("turn_index", 0)
        if observation.get("turns_remaining", 0) <= 20:
            cx, cy = w // 2, h // 2
            score += 2 * (-(abs(nx - cx) + abs(ny - cy)))

        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move