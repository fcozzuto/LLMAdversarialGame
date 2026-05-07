def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set((p[0], p[1]) for p in obstacles)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def key_for_target(rx, ry):
        my_d = man(sx, sy, rx, ry)
        op_d = man(ox, oy, rx, ry)
        return (op_d - my_d, -my_d, -rx, -ry)

    # Choose our best target based on current distance advantage.
    best_t = None
    best_key = None
    for rx, ry in resources:
        k = key_for_target(rx, ry)
        if best_key is None or k > best_key:
            best_key, best_t = k, (rx, ry)
    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    # If we are already on the target, just move to the next best target by advantage.
    if sx == tx and sy == ty and len(resources) > 1:
        best_t = None
        best_key = None
        for rx, ry in resources:
            if rx == tx and ry == ty:
                continue
            k = key_for_target(rx, ry)
            if best_key is None or k > best_key:
                best_key, best_t = k, (rx, ry)
        tx, ty = best_t

    cur_my = man(sx, sy, tx, ty)
    cur_op = man(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        my_next = man(nx, ny, tx, ty)
        # Estimate opponent pressure: reduce our advantage on this target less is better.
        adv_next = cur_op - my_next
        # Tie-breakers: prefer reducing distance, then deterministic coordinate order.
        score = (adv_next, -my_next, -nx, -ny)
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]