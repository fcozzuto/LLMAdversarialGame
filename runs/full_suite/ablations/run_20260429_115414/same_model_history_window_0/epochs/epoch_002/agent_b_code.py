def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If we're on a resource, stay.
    for rx, ry in resources:
        if rx == sx and ry == sy and (rx, ry) not in obstacles:
            return [0, 0]

    best_target = None
    best_key = None

    # Pick a target resource: prefer reach advantage over opponent, then closer.
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - myd, -myd, -(abs(rx - sx) + abs(ry - sy)))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else (sx, sy)

    # Choose move that improves toward target while avoiding collisions and nearby opponent.
    best_move = None
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Penalize stepping adjacent/onto opponent vicinity.
        danger = 1000 if d_opp <= 1 else 0
        # Prefer maximizing distance we can gain vs opponent at new position.
        myd_new = cheb(nx, ny, tx, ty)
        opd_new = cheb(ox, oy, tx, ty)
        key = (-(d_to_t + danger), -(opd_new - myd_new), -cheb(nx, ny, sx, sy))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]