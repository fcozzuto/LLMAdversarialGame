def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def man(ax, ay, bx, by):
        d1 = ax - bx; d2 = ay - by
        if d1 < 0: d1 = -d1
        if d2 < 0: d2 = -d2
        return d1 + d2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0); best_val = -10**18

    # Determine which row the opponent is likely sweeping to prioritize denial.
    sweep_row = oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Obstacle pressure: avoid moving adjacent to obstacles (softly).
        adj_obs = 0
        for ox2, oy2 in obstacles:
            if man(nx, ny, ox2, oy2) == 1:
                adj_obs += 1

        move_best = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # If we can arrive first, strongly prefer it; otherwise deny resources opponent is closer to.
            win_term = (do - ds)  # positive if we are closer
            deny_row = 1 if ry == sweep_row else 0
            # Prefer resources that are "left" for our corner: bias by owning vs opponent corner.
            corner_bias = (rx + ry) if (sx + sy) <= (ox + oy) else (-(rx + ry))
            # Tie-break deterministically.
            tie = -(rx * 0.001 + ry * 0.002)
            val = win_term * 1000 + corner_bias + deny_row * 15 + tie - adj_obs * 3 - ds
            if val > move_best:
                move_best = val

        # Slightly discourage staying still unless it's best.
        if dx == 0 and dy == 0:
            move_best -= 0.5

        if move_best > best_val:
            best_val = move_best
            best = (dx, dy)

    return [int(best[0]), int(best[1])]