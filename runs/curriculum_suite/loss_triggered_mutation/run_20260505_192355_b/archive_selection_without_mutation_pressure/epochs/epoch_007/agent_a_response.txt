def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    legal_moves = [(dx, dy) for dx, dy in moves if legal(sx + dx, sy + dy)]
    if not legal_moves:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def edge_bonus(x, y):
        d = min(x, w - 1 - x, y, h - 1 - y)
        return 2 if d == 0 else (1 if d == 1 else 0)

    if not resources:
        best = legal_moves[0]
        bestv = -10**18
        for dx, dy in legal_moves:
            nx, ny = sx + dx, sy + dy
            v = -man(nx, ny, ox, oy) + 2 * edge_bonus(nx, ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Prefer resources I can reach earlier than the opponent; keep distance from opponent lightly.
    best = legal_moves[0]
    bestv = -10**18
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        my_to_op = man(nx, ny, ox, oy)
        my_best = 10**9
        opp_best = 10**9
        take_score = 0
        for rx, ry in resources:
            dm = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if dm < my_best:
                my_best = dm
            if do < opp_best:
                opp_best = do
            # If I can reach first, strongly reward; if opponent reaches first, penalize a bit.
            if dm <= do:
                take_score += 30 - 3 * dm
            else:
                take_score -= 2 + (dm - do)
        # Combine: quicker collection, deny opponent, avoid getting trapped near them, edge preference.
        v = (40 - 5 * my_best) + take_score + 1.5 * (opp_best - 2 * edge_bonus(nx, ny)) - 0.6 * my_to_op
        if v > bestv:
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]