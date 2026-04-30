def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = {(p[0], p[1]) for p in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource: race ones where we're closer; otherwise pick closest-to-us.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        race_adv = op_d - my_d
        if best_key is None:
            best_key = (-10**9, 10**9, 10**9)
            best_t = (rx, ry)
        if my_d <= op_d:
            key = (race_adv, -my_d, rx + ry * 0.0001)
            if best_key is None or key > best_key:
                best_key, best_t = key, (rx, ry)
        elif best_t is None or not isinstance(best_t, tuple):
            pass

    if best_t is None or (best_key[0] < 0 and best_key is not None):
        best_t = None
        best_d = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_t):
                best_d = d
                best_t = (rx, ry)

    tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_util = None

    cur_op_d = cheb(ox, oy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        my_next_d = cheb(nx, ny, tx, ty)
        # Favor moves that improve race advantage; break ties by progress.
        util = (cur_op_d - my_next_d) * 5 - my_next_d
        if best_util is None or util > best_util:
            best_util = util
            best_move = (dx, dy)
        elif util == best_util:
            # Prefer smaller distance; then prefer non-staying.
            cur_best_d = cheb(sx + best_move[0], sy + best_move[1], tx, ty)
            if my_next_d < cur_best_d or (my_next_d == cur_best_d and best_move == (0, 0) and (dx, dy) != (0, 0