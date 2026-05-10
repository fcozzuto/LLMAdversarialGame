def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # If opponent can reach sooner, deprioritize; also avoid competing on their likely sweep row.
        comp = od - sd
        offrow = abs(ry - oy)
        # Prefer closer targets when tie-breaking.
        key = (-(comp <= 0), comp, -offrow, sd, rx, ry)
        # Key ordering: best_key minimal; so make "good" small.
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # One-step improvement with a simple evaluation among all valid moves.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = [0, 0]
    best_eval = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        # Disallow moving onto opponent position if possible (engine would keep us, but we avoid it).
        if (nx, ny) == (ox, oy):
            continue

        # If we are adjacent/diagonal to a resource, prioritize picking the best among resources for this move.
        cur_best = None
        cur_key = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            comp = od - sd
            offrow = abs(ry - oy)
            # Want we reach sooner (comp <= 0), also maximize offrow (avoid their sweep line).
            key = (-(comp <= 0), comp, -offrow, sd, rx, ry)
            if cur_key is None or key < cur_key:
                cur_key = key
                cur_best = (rx, ry)
        # Smaller key is better.
        if best_eval is None or cur_key < best_eval:
            best_eval = cur_key
            best_mv = [mdx, mdy]

    return best_mv