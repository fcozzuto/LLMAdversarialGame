def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick target with best "we are closer than opponent" advantage (or least disadvantage).
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = man(sx, sy, rx, ry)
        op_d = man(ox, oy, rx, ry)
        key = (op_d - my_d, -my_d, -rx, -ry)
        if best_key is None or key > best_key:
            best_key, best_t = key, (rx, ry)
    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        return (nx, ny) not in obs

    best_move = [0, 0]
    best_val = None

    my_d0 = man(sx, sy, tx, ty)
    op_d0 = man(ox, oy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = man(nx, ny, tx, ty)
        op_d = op_d0  # opponent move unknown; keep stable

        # Primary: improve our advantage by getting closer to target.
        adv_gain = (op_d - my_d) - (op_d - my_d0)
        # Secondary: reduce distance to target.
        val = (adv_gain, -my_d, -abs(nx - ox) - abs(ny - oy), -((nx, ny) == (tx, ty)))
        if best_val is None or val > best_val:
            best_val, best_move = val, [dx, dy]

    # If all moves blocked (unlikely), stay.
    if best_val is None:
        return [0, 0]
    return best_move