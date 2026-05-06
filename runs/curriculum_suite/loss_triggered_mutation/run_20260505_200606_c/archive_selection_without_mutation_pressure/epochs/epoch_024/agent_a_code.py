def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        move_score = 0
        # Encourage keeping options open and cutting time to contested resources
        center_pen = abs(nx - cx) + abs(ny - cy)
        move_score -= 0.15 * center_pen

        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            # If opponent can reach sooner, prioritize contesting/blocking by closing the gap.
            gap = opp_d - our_d  # positive => we arrive no later than opponent
            if gap >= 0:
                contest_bonus = 6
            else:
                contest_bonus = 0

            row_gap = abs(ny - ry)
            row_bonus = 4 if row_gap == 0 else (2 if row_gap == 1 else (1 if row_gap == 2 else 0))

            # Also prefer approaching resources that are currently "hot" for the opponent.
            opp_hot = (opp_d <= min(man(ox, oy, r2x, r2y) for (r2x, r2y) in resources))
            hot_bonus = 2 if opp_hot else 0

            # Net: contest time advantage + mild row alignment + hot targeting
            move_score += (2.2 * gap) + contest_bonus + row_bonus + hot_bonus - 0.08 * our_d

        if move_score > best_score:
            best_score = move_score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]