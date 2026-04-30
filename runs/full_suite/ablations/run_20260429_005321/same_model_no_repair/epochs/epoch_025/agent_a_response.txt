def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_best = min(man(ox, oy, r[0], r[1]) for r in resources)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"]):
            continue
        if (nx, ny) in obstacles:
            score = -10**6
        else:
            self_best = min(man(nx, ny, r[0], r[1]) for r in resources)
            score = (opp_best - self_best) * 10 - (self_best)
            # slight preference to move generally toward the nearest resource
            r0 = resources[0]
            d0 = man(sx, sy, r0[0], r0[1])
            d1 = man(nx, ny, r0[0], r0[1])
            score += (d0 - d1) * 0.01
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]
    return best_move