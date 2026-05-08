def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if resources:
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            my_best = None
            opp_best = None
            # For each resource, prefer moves where we become closer than opponent.
            for rx, ry in resources:
                myd = dist8(nx, ny, rx, ry)
                opd = dist8(nx, ny, rx, ry)
                # my_advance is positive if we are closer to that resource than opponent.
                adv = opd - myd
                if my_best is None or (adv, -myd) > (my_best, -my_best2):
                    my_best = adv
                    my_best2 = myd
                    opp_best = opd
            adv = my_best
            myd = my_best2
            opd = opp_best
            # Encourage larger lead; tie-break: faster arrival; slight penalty if too close to opponent position.
            opp_to_me = dist8(nx, ny, ox, oy)
            val = (adv * 1000) + (-myd * 10) + (-opp_to_me)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: head to an opponent-side corner deterministically.
    # Choose corner that is forward in y if possible, otherwise toward the nearer x-side.
    forward_corner = (w - 1, h - 1) if sx <= (w - 1) // 2 else (0, h - 1)
    tx, ty = forward_corner
    if sx >= (w - 1) // 2:
        ty = 0 if sy <= (h - 1) // 2 else h - 1  # alternate deterministically by side

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = dist8(nx, ny, tx, ty)
        opd = dist8(nx, ny, ox, oy)
        # Prefer decreasing distance to target; also avoid getting too close to opponent.
        val = (-myd * 10) + (-opd)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]