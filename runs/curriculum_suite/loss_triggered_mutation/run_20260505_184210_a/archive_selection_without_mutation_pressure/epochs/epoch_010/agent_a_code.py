def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    # If no resources, head toward center while staying safe.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, cx, cy)
            key = (d, dx, dy)
            if best is None or key < best:
                best = key
        return [best[1], best[2]]

    opp_closest_d = None
    # Determine opponent's most dangerous resource (closest to opponent).
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if opp_closest_d is None or d < opp_closest_d:
            opp_closest_d = d
    opp_danger = opp_closest_d

    best_key = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Score this move by the best resource we can contest.
        local_best = None
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - our_d  # positive means we are at least as fast
            # Prefer securing (margin positive), then smaller our_d, then smaller opp_d.
            key = (-1 if margin > 0 else 1, -margin, our_d, opp_d, rx, ry)
            if local_best is None or key < local_best:
                local_best = key

        # Add a defensive tie-break: if opponent is about to be very close to any resource,
        # prefer moves that avoid worsening that proximity too much.
        # (Using next-cell distance from opponent to the closest resource is stable/deterministic.)
        defensive = 0
        if opp_danger is not None:
            # Encourage moves that reduce our own distance to the same dangerous resources.
            # This indirectly blocks opponent by keeping us near likely contested targets.
            defensive = 0

        # Combine.
        key = (local_best[0], local_best[1], local_best[2], local_best[3], defensive, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]