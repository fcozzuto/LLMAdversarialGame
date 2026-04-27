def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)

    if not resources:
        # No resources: fall back to tightening around opponent
        dx = -1 if ox < sx else (1 if ox > sx else 0)
        dy = -1 if oy < sy else (1 if oy > sy else 0)
        return [dx, dy]

    # Choose a target deterministically: nearest resource to self (tie -> lexicographically smallest)
    best_t = None
    best_d = None
    for rx, ry in resources:
        d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_t):
            best_d = d
            best_t = (rx, ry)
    tx, ty = best_t

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Avoid stepping into obstacles; engine would keep in place, but penalize to be safe
        if (nx, ny) in obs_set:
            continue
        # Bounds: engine likely keeps in place if invalid, but penalize out-of-bounds strongly
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue

        my_d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        opp_d = (tx - ox) * (tx - ox) + (ty - oy)  # opponent not moved this turn
        # If we can potentially grab resource this turn, prioritize it
        on_resource = (nx, ny) == (tx, ty)
        # Slight tie-breakers to reduce dithering: prefer smaller move distance to center if scores equal
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        # Maximize advantage: lower my_d, higher relative to opponent
        score = (1000000 if on_resource else 0) + (opp_d - my_d) - 0.001 * center_pen

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all obstacle-bound filtered out, allow staying or a safe move by ignoring bounds/obstacles
    if best_score is None:
        dx = -1 if tx < sx else (1 if tx > sx else 0)
        dy = -1 if ty < sy else (1 if ty > sy else 0)
        return [dx, dy]

    return [best_move[0], best_move[1]]