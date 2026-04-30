def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation["obstacles"]}
    resources = [tuple(p) for p in observation["resources"]]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not resources:
        # drift toward center and away from opponent a bit
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_val = None
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            val = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy) - 0.15 * ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate by best resource we can reach competitively.
        # Lower is better.
        best_r_val = None
        for rx, ry in resources:
            d_self = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
            d_opp = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)

            # Encourage resources where we are closer or can undercut soon.
            # Also add a mild preference for nearer overall.
            competitive_bonus = 0
            if d_self <= d_opp:
                competitive_bonus -= 12
                if d_self == 0:
                    competitive_bonus -= 50
            else:
                # Discourage chasing resources opponent is clearly closer to.
                competitive_bonus += min(20, (d_opp - d_self) * 0.03)

            # Prefer moves that reduce our distance to the best resource.
            r_val = d_self * 1.0 + d_opp * 0.08 + competitive_bonus
            if best_r_val is None or r_val < best_r_val:
                best_r_val = r_val

        # Tie-break: prefer smaller distance to current nearest resource center-of-mass.
        # (Deterministic, cheap.)
        # Compute once per move using the nearest resource to us.
        nearest_sq = None
        for rx, ry in resources:
            d = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
            if nearest_sq is None or d < nearest_sq:
                nearest_sq = d

        move_val = best_r_val + nearest_sq * 0.005

        if best_val is None or move_val < best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]