def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic: scan moves in fixed order; break ties by lexicographic (dx,dy).
    best_move = [0, 0]
    best_score = None
    # Also track a small "global" preference for being closer to the best contested resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate move by best contested resource, not just closest.
        # Favor immediate pickup strongly.
        move_best = -10**9
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                val = 10**8
            else:
                # Main contest: how much earlier we arrive.
                # Larger (do - ds) means we are closer/sooner than opponent.
                val = (do - ds) * 200 - ds * 5 + (w + h - (abs(rx - nx) + abs(ry - ny))) * 0.01
            if val > move_best:
                move_best = val

        # Secondary: maximize safety against giving opponent a near-term advantage
        # by reducing the opponent's best contested gain.
        opp_gain = 10**9
        for rx, ry in resources:
            dso = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            gain = do - dso
            if gain < opp_gain:
                opp_gain = gain

        score = move_best + opp_gain * 2

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move