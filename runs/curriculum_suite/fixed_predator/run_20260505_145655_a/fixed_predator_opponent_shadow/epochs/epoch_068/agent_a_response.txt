def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dir = (0, 0)
    best_score = -10**18

    # Pick best target by "opponent advantage" minus our distance (deterministic tie breaks by position)
    best_t = resources[0]
    best_tv = -10**18
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        tv = (d_opp - d_me) * 1000 - d_me
        if tv > best_tv or (tv == best_tv and (ty, tx) < (best_t[1], best_t[0])):
            best_tv = tv
            best_t = (tx, ty)
    tx, ty = best_t

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        d_me = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)

        # Strong preference: move that keeps/creates an advantage, also reduce our distance.
        advantage = d_opp - d_me
        score = advantage * 2000 - d_me

        # Secondary: avoid stepping into "bad" cells relative to other resources (simple gradient)
        # and discourage moves that would let opponent be closer by a large margin.
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) == (tx, ty):
                continue
            opp_close = (abs(rx - ox) + abs(ry - oy)) - (abs(rx - nx) + abs(ry - ny))
            if opp_close > 0:
                score -= opp_close * 20

        # Tertiary: deterministic tie-break favor staying directionally toward target
        score += -3 * (abs(tx - nx) - abs(tx - x) + abs(ty - ny) - abs(ty - y))

        if score > best_score or (score == best_score and (dy, dx) < (best_dir[1], best_dir[0])):
            best_score = score
            best_dir = (dx, dy)

    return [int(best_dir[0]), int(best_dir[1])]