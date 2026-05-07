def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, None)  # (score tuple, move)

    # Choose a primary target by "who can reach it first" advantage.
    # Prefer targets where we reduce the opponent lead (or gain it).
    primary = None
    best_primary = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd)  # maximize adv, then smaller sd
        if best_primary is None or key > best_primary:
            best_primary = key
            primary = (rx, ry)
    prx, pry = primary

    # Score each move by how much it improves our race on the primary target,
    # plus a small denier term to contest the best opponent target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        sd_t = md(nx, ny, prx, pry)
        od_t = md(ox, oy, prx, pry)
        # Best-denial advantage from this next position (max over resources).
        # This prevents drifting into a losing direction when target is contested.
        best_den = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            key = (adv, -sd)
            if best_den is None or key > best_den:
                best_den = key
        best_adv = best_den[0] if best_den is not None else (od_t - sd_t)

        # Primary score: first maximize (opponent lead reduction / win chance)
        # then maximize overall denial and minimize our distance to primary.
        score = (od_t - sd_t, best_adv, -sd_t)
        if best_move[0] is None or score > best_move[0]:
            best_move = (score, [dx, dy])

    return best_move[1] if best_move[1] is not None else [0, 0]