def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best_r = None
        best_key = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            key = (sd - od, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r

    best_move = (0, 0)
    best_val = -10**18
    base_sd = man(sx, sy, tx, ty)
    base_od = man(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in occ:
            continue
        nsd = man(nx, ny, tx, ty)
        # Greedy race: maximize (opponent advantage gap) while reducing our distance; avoid obstacles by discouraging detours.
        self_improve = base_sd - nsd
        opp_gap = (base_od - nsd)  # higher means we're closer than opponent would be to this target at current turn heuristic
        obstacle_adj_pen = 0
        if resources:
            # small penalty if we move "away" from target compared to our best adjacent progress
            obstacle_adj_pen = 0.2 * (nsd - base_sd if nsd > base_sd else 0)
        # Encourage alignment with target (diagonal helps) and prevent oscillation: prefer moves that strictly reduce nsd when possible.
        val = 10 * self_improve + 2 * (opp_gap) - 0.05 * nsd - obstacle_adj_pen
        if resources and nsd == 0:
            val += 1e6
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move == (0, 0) and (sx, sy) in occ:
        # If somehow inside obstacle (shouldn't happen), try any safe neighbor.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in occ:
                return [dx, dy]
    return [best_move[0], best_move[1]]