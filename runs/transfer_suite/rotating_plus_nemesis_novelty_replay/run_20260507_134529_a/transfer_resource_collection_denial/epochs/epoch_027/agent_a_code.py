def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer states where we can arrive first (big opd-myd), then by proximity.
        key = (opd - myd, -myd, -opd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    best_move = (0, 0)
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Main: improve our "race" advantage for target.
        race = opd2 - myd2
        # Secondary: prevent letting opponent gain too much (use their dist to our candidate cell).
        opp_reach_to_us = cheb(ox, oy, nx, ny)
        # Tertiary: keep movement meaningful (closer to target).
        closeness = -myd2
        # Quaternary: deterministic tie-break by position.
        key = (race, closeness, -opp_reach_to_us, -nx, -ny)
        if best_eval is None or key > best_eval:
            best_eval = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]