def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = -10**18
    best_tie = (10**9, 10**9)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # For the move, pick the best resource to pursue (favor unguarded: we are closer).
        local_best = -10**18
        local_gap = -10**18
        local_selfd = 10**9
        local_opd = 10**9

        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            gap = do - ds  # positive => we are closer
            # Denier tends to snatch closest; prefer resources where we stay ahead,
            # otherwise still chase the least-losing option.
            val = gap * 12 - ds * 2 + min(do, 20) * (1 if gap > 0 else -1)
            if val > local_best or (val == local_best and (gap, -ds) > (local_gap, -local_selfd)):
                local_best = val
                local_gap = gap
                local_selfd = ds
                local_opd = do

        # Move tie-breakers: higher gap first, then smaller self distance, then larger opponent distance.
        move_tie = (-local_gap, local_selfd, -local_opd)
        if local_best > best_val or (local_best == best_val and move_tie < best_tie):
            best_val = local_best
            best_move = [dx, dy]
            best_tie = move_tie

    return best_move