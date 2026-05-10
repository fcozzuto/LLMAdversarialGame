def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    # Fast sets for exact pickup detection
    res_set = set((r[0], r[1]) for r in resources) if resources else set()

    # If no resources, drift to center-ish deterministic
    if not resources:
        tx, ty = W // 2, H // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_move = [0, 0]
    best_score = -10**18

    # Precompute opponent distances to each resource
    opp_d = {}
    for rx, ry in resources:
        opp_d[(rx, ry)] = abs(ox - rx) + abs(oy - ry)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Immediate pickup
        gain = 0
        if (nx, ny) in res_set:
            gain = 10000

        # Evaluate best resource to target from this landing cell
        my_best = 10**9
        desirability = -10**9
        for rx, ry in resources:
            dme = abs(nx - rx) + abs(ny - ry)
            dob = opp_d[(rx, ry)]
            # Prefer resources where we are strictly closer; if tie, still prefer closer to reduce race risk
            race = (dob - dme)
            # Combine: closer to us, and race advantage
            score = race * 300 - dme * 5
            if score > desirability:
                desirability = score
                my_best = dme

        # Small deterrent to move far away from opponent when racing is unclear
        opp_pull = -((abs(nx - ox) + abs(ny - oy)) // 2)

        # Bonus for choosing a move that reduces distance to our currently best resource
        score_total = gain + desirability + opp_pull
        if score_total > best_score:
            best_score = score_total
            best_move = [dx, dy]

    return best_move