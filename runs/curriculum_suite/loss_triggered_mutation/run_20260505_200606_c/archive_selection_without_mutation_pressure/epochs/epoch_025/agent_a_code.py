def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(ax, ay, bx, by):
        ax = ax - bx
        ay = ay - by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    best_dxdy = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        center_pen = abs(nx - cx) + abs(ny - cy)
        local_best = -10**18
        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            # Intercept/race: prefer resources we can reach earlier, with row alignment as a tie-break.
            row_gap = abs(ny - ry)
            row_bonus = 3.0 if row_gap == 0 else (2.0 if row_gap == 1 else (1.0 if row_gap == 2 else 0.0))
            gain = 2.2 * (opp_d - our_d) + row_bonus

            # Strongly prioritize immediate pickup.
            if our_d == 0:
                gain += 20.0

            if gain > local_best:
                local_best = gain

        val = local_best - 0.15 * center_pen
        if val > best_val or (val == best_val and (dx, dy) < best_dxdy):
            best_val = val
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]