def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))  # Chebyshev

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Pick a target resource where we are (as deterministically as possible) earlier than opponent.
    best = None
    best_key = None
    if resources:
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Key: strongly prefer resources we can reach earlier; then closer ourselves;
            # then farther from opponent; then stable tie-break by coordinates.
            reach_diff = do - ds  # positive is good
            key = (-(reach_diff), ds, -do, rx, ry)
            # Because we used negative of reach_diff: smaller key[0] means larger reach_diff.
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
    if best is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    # Choose a move that reduces distance to target, avoids giving opponent immediate access.
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in legal:
        my_d = dist(nx, ny, tx, ty)
        opp_immediate = dist(ox, oy, tx, ty) - dist(nx, ny, tx, ty)
        # Penalize stepping away; penalize moving into squares that are "too close" to opponent.
        opp_close = max(0, 3 - dist(nx, ny, ox, oy))
        # Add small preference to move along axes deterministically (reduces dithering).
        axis_pref = 0 if (dx == 0 or dy == 0) else 1
        # Score: lower is better.
        score = (my_d, opp_immediate, opp_close, axis_pref, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]