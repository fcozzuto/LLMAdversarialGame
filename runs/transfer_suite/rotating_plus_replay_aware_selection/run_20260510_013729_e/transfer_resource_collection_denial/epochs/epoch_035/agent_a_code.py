def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}

    def cheb(a, b, c, d):
        dx = c - a
        if dx < 0:
            dx = -dx
        dy = d - b
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # If we can beat some resource (closer or equal vs opponent), target the best such one.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive => we are closer (or tie) to this resource
        # Prefer larger advantage, then smaller our distance, then deterministic coordinate tie-break.
        key = (adv, -ds, -(rx * 8 + ry))
        if best is None or key > best:
            best = key + (rx, ry)

    target_x, target_y = best[-2], best[-1]
    # If advantage is negative for all, fall back to best chase by opponent-relative distance (still deterministic).
    if best[0] < 0:
        best2 = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer minimizing (ds - do): we want to reduce opponent lead, but chase the best compromise.
            key2 = (-(ds - do), -ds, (rx * 8 + ry))
            if best2 is None or key2 > best2:
                best2 = key2 + (rx, ry)
        target_x, target_y = best2[-2], best2[-1]

    # Choose among legal deltas by evaluating resulting cell toward target and away from opponent.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        ds1 = cheb(nx, ny, target_x, target_y)
        do1 = cheb(ox, oy, target_x, target_y)
        # Also add mild obstacle-free preference by penalizing closeness to nearest obstacle cell.
        min_obst = 99
        for (ax, ay) in obstacles:
            d = abs(ax - nx) + abs(ay - ny)
            if d < min_obst:
                min_obst = d
        score = (do1 - ds1, -ds1, min_obst, -(dx * 2 + dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]