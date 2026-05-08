def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    blocked = {(p[0], p[1]) for p in obstacles}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(a, b, x, y):
        return abs(a - x) + abs(b - y)

    # Pick a target resource where we are likely to arrive no later than the opponent.
    target = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we can secure: maximize (od - sd), then prefer lower sd.
        key = (od - sd, -sd)
        if best_key is None or key > best_key:
            best_key = key
            target = (rx, ry)

    # If no resources, try to reduce distance to opponent.
    if target is None:
        best_move = (0, 0)
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            val = man(nx, ny, ox, oy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = target

    # Score each possible move with short lookahead:
    # - Primary: get closer to target.
    # - Secondary: maintain/strengthen lead over opponent for that target.
    # - Tertiary: slight bias away from opponent position to deny.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        my_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Lead improves when (opp_d - my_d) increases; higher is better.
        score = (opp_d - my_d, -my_d, -man(nx, ny, ox, oy) * 0.01)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]