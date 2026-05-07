def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Greedy one-step lookahead: maximize advantage to the best contested resource.
    # Advantage for a resource r: opp_dist - self_dist (bigger is better).
    best_move = None
    best_score = None
    best_tie = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        local_best_adv = -10**9
        local_best_self = 10**9
        for rx, ry in res_set:
            ds = manh(nx, ny, rx, ry)
            do = manh(ox, oy, rx, ry)
            adv = do - ds
            if adv > local_best_adv or (adv == local_best_adv and ds < local_best_self):
                local_best_adv = adv
                local_best_self = ds
        # If nothing improves advantage (all negative), fall back to nearest resource.
        if len(res_set) == 0:
            return [0, 0]

        score = local_best_adv
        tie = local_best_self

        if best_score is None or score > best_score or (score == best_score and tie < best_tie):
            best_score = score
            best_tie = tie
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]