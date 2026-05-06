def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def man(ax, ay, bx, by):
        ax = ax - bx
        if ax < 0:
            ax = -ax
        ay = ay - by
        if ay < 0:
            ay = -ay
        return ax + ay

    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        # Immediate interception/blocking: prioritize moves that align y with a resource
        # where opponent is currently closer.
        for rx, ry in resources:
            opp_d = man(ox, oy, rx, ry)
            our_d = man(nx, ny, rx, ry)
            row_gap = abs(ny - ry)
            # If we can compete on this resource's row, boost strongly.
            compete = (our_d <= opp_d)
            row_bonus = 20 if row_gap == 0 else 12 if row_gap == 1 else 6 if row_gap == 2 else 0
            lead = opp_d - our_d  # positive if we are closer
            val += row_bonus
            val += 8 * lead if compete else 3 * lead
            # Slight penalty if we'd give up the y-alignment opportunity to the opponent.
            opp_row_gap = abs(oy - ry)
            if opp_row_gap == 0 and row_gap > 0:
                val -= 10

        # Tie-breaker: prefer moving toward center-ish and away from obstacles lightly
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val -= 0.01 * man(nx, ny, int(cx), int(cy))
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]