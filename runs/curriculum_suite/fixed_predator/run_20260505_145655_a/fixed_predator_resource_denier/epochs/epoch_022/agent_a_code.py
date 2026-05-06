def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Prefer cells that (1) approach some resource we beat the opponent for, (2) reduce
    # opponent access to the "most valuable" remaining resource by moving closer to it.
    best = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        my_step_d = abs(nx - ox) + abs(ny - oy)
        local = 0.0

        # Evaluate each resource; take best for us and best "denial threat" for opponent.
        us_best = -10**18
        opp_best = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)

            # Strongly reward overtaking opportunities; penalize losing races.
            # Add slight preference for closer resources.
            race = (oppd - selfd)
            sc_us = race * 10 - selfd * 0.7
            if sc_us > us_best:
                us_best = sc_us

            # Deny: if opponent is closer/equally close, we want to get closer too,
            # but still prioritize our own overtakes via weighting below.
            sc_opp = (selfd - oppd) * 6 - selfd * 0.2
            if sc_opp > opp_best:
                opp_best = sc_opp

        local = us_best * 1.2 + opp_best * 0.8
        # Mildly control center-ish moves to avoid local traps.
        local += -0.05 * ((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2)
        # If we can simultaneously reduce opponent distance, do it.
        local += -0.03 * my_step_d

        if local > best_score:
            best_score = local
            best = [dx, dy]

    return [int(best[0]), int(best[1])]