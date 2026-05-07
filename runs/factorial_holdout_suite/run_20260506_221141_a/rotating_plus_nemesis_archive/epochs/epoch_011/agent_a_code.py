def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not res:
        return [0, 0]

    # Opponent's nearest-resource target (deterministic tie-break by distance then coordinates)
    best_op = None
    for r in res:
        rx, ry = r[0], r[1]
        d = man(ox, oy, rx, ry)
        key = (d, rx, ry)
        if best_op is None or key < best_op[0]:
            best_op = (key, rx, ry)
    tx, ty = best_op[1], best_op[2]

    # Choose move that most improves our ability to reach opponent's likely target first,
    # with fallback to best overall nearest resource.
    best_move = None
    best_fallback = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_us_to_t = man(nx, ny, tx, ty)
        d_op_to_t = man(ox, oy, tx, ty)
        # Primary: maximize advantage in reaching target (opponent greedy baseline minus ours)
        adv = d_op_to_t - d_us_to_t
        # Secondary: minimize our distance to any resource (avoid falling behind)
        d_us_any = None
        for r in res:
            rx, ry = r[0], r[1]
            dd = man(nx, ny, rx, ry)
            if d_us_any is None or dd < d_us_any[0]:
                d_us_any = (dd, rx, ry)
        key_primary = (-adv, d_us_to_t, d_us_any[0], nx, ny)
        if best_move is None or key_primary < best_move[0]:
            best_move = (key_primary, dx, dy)

        key_fb = (d_us_any[0], d_us_any[1], d_us_any[2], nx, ny)
        if best_fallback is None or key_fb < best_fallback[0]:
            best_fallback = (key_fb, dx, dy)

    if best_move is not None:
        return [best_move[1], best_move[2]]
    return [best_fallback[1], best_fallback[2]] if best_fallback is not None else [0, 0]