def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    res = [(int(x), int(y)) for x, y in resources]
    # Prefer strategies that let us reach a resource before the opponent.
    # Tie-breaker: also mildly avoid staying too close to opponent to reduce contested pickups.
    best = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        myd_opp_gain = -10**18
        for tx, ty in res:
            myd = man(nx, ny, tx, ty)
            opd = man(ox, oy, tx, ty)

            # Base: win chance = (opponent distance - my distance)
            # Higher is better. Add tiny preference for closer resources.
            sc = (opd - myd) * 100 - myd

            # If very close to target, slightly reduce opponent contest by preferring far-opponent.
            if myd == 0:
                sc += (opd * 10)
            elif myd == 1:
                sc += (opd * 2)

            if sc > myd_opp_gain:
                myd_opp_gain = sc

        # Additional term: keep some separation unless it conflicts with target urgency.
        sep = man(nx, ny, ox, oy)
        sep_term = sep  # more separation better
        cand_sc = myd_opp_gain + sep_term

        if cand_sc > best_sc:
            best_sc = cand_sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]