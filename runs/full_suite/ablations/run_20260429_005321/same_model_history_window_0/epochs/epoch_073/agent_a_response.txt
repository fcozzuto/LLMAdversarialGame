def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obstacle_set = set((x, y) for x, y in obstacles)
    move_options = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h

    # If on a resource, try to hold position to collect (engine likely keeps/collects if already there)
    if (sx, sy) in set((x, y) for x, y in resources):
        return [0, 0]

    res_set = set((x, y) for x, y in resources)
    target = None
    best_d = None
    for (rx, ry) in resources:
        d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        if best_d is None or d < best_d:
            best_d = d
            target = (rx, ry)

    # If no resources left, play positional: move away from opponent a bit while going center-ish
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_score = None
        for dx, dy in move_options:
            nx, ny = sx + dx, sy + dy
            if not clamp_in(nx, ny) or (nx, ny) in obstacle_set:
                continue
            # Prefer closer to center, but also slightly away from opponent
            center_d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            opp_d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = -center_d + 0.15 * opp_d
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    tx, ty = target
    opp_d_now = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)

    # Evaluate moves: prioritize stepping onto resources; then minimize distance to nearest resource;
    # tie-break deterministically by maximizing distance from opponent and by move preference order.
    preference = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            preference.append((dx, dy))
    pref_index = {m: i for i, m in enumerate(preference)}

    best_move = (0, 0)
    best_score = None
    for dx, dy in move_options:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny) or (nx, ny) in obstacle_set:
            continue

        if (nx, ny) in res_set:
            return [dx, dy]

        # Distance to nearest resource after move
        min_res_d = None
        for (rx, ry) in resources:
            d = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
            if min_res_d is None or d < min_res_d:
                min_res_d = d

        # Encourage approach to target resource and optionally contest opponent if close
        to_target_d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        opp_d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        contest = 0.0
        if opp_d_now < 10:  # opponent relatively close
            contest = 0.08 * (opp_d_now - opp_d)  # slightly prefer moves that reduce opponent distance

        score = (-min_res_d) + (-0.08 * to_target_d) + (0.06 * opp_d) + contest
        # deterministic tie-break: prefer lower index in preference
        if best_score is None or score > best_score or (score == best_score and pref_index[(dx, dy)] < pref_index[best_move]):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]