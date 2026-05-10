def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_val = None

    # Evaluate one-step moves by best attainable "lead" over opponent on any resource.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # small penalty for moving away from the opponent-target corridor (resource denial).
        lead_best = -10**9
        dist_sum_best = 10**9
        same_row_best = 0
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            lead = do - ds  # positive => we are closer than opponent
            # Strongly prioritize grabbing resources where we can deny (lead > 0), but also
            # allow "set up" moves when no deny is possible.
            lead_score = lead * 2.0
            if ry == oy:
                lead_score += 1.0  # contest opponent's current row
            if rx == ox:
                lead_score += 0.3  # slight vertical contest bias
            # Tie-break: prefer nearer resources to avoid dithering.
            dist_score = ds * 0.07 + (0.0 if ds == 0 else 0.0)
            val = lead_score - dist_score

            if (val > lead_best) or (val == lead_best and ds + do < dist_sum_best) or (val == lead_best and ds + do == dist_sum_best and ry == oy):
                lead_best = val
                dist_sum_best = ds + do
                same_row_best = 1 if ry == oy else 0

        # Prefer immediate progress when lead is tied.
        # Also, lightly avoid crossing to far side unless it improves deny lead.
        opp_cross_pen = 0.0
        if (ox - sx) * (ox - nx) < 0:
            opp_cross_pen = 0.15
        # Encourage not to get stuck: slight preference to reduce own distance to best resource overall.
        local_dist_min = min(man(nx, ny, rx, ry) for rx, ry in resources)
        val_total = lead_best - opp_cross_pen - local_dist_min * 0.01 - (0.03 * (1 if dx == 0 and dy == 0 else 0)) + same_row_best * 0.02

        if best_val is None or val_total > best_val:
            best_val = val_total
            best_move = [dx, dy]

    if best_move == [0, 0]:
        # If all moves filtered out (shouldn't happen), stay.
        return [0, 0]
    return best_move