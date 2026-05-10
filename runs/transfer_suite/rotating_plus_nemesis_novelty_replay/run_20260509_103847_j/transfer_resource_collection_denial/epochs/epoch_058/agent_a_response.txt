def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    tr = observation.get("turns_remaining", 0)
    opp_time_bias = 1.0 + (0.15 if tr < 8 else 0.0)  # slightly more aggressive late

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate the move by the best "secured-advantage" resource we can pursue.
        best_for_move = -10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources we can reach not later than opponent; otherwise contest.
            if ds <= do:
                # stronger when ds is smaller and gap is larger; also slight urgency
                val = (do - ds) * 10 + (12 - ds) + (1 if ds == 0 else 0)
            else:
                # if we can't beat them, still try to reduce their lead and deny nearby
                val = -(ds - do) * 10 + (8 - ds)
            # discourage targets that are essentially unreachable soon
            if ds > tr + 2:
                val -= 50
            if val > best_for_move:
                best_for_move = val

        key = (best_for_move, -man(nx, ny, ox, oy), -man(nx, ny, sx, sy), dx, dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = [dx, dy]

    # If all moves were filtered out (shouldn't happen), stay.
    return best_move if best_val is not None else [0, 0]