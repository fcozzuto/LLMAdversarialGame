def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    moves.append((0, 0))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def obstacle_pen(x, y):
        pen = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                pen += 3
        return pen

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            myd = man(nx, ny, tx, ty)
            key = (myd, obstacle_pen(nx, ny))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    best_move = (None, 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_target_val = None
        for rx, ry in resources:
            myd_now = man(nx, ny, rx, ry)
            opd_now = man(ox, oy, rx, ry)
            rel = opd_now - myd_now  # positive => we are closer
            # prefer resources where we can gain or at least not lose much
            dist_bias = -man(sx, sy, rx, ry)  # closer now tends to be better
            # small tie-break to avoid cornering into obstacles
            val = (rel * 10) + (dist_bias) - obstacle_pen(nx, ny) * 0.3
            if best_target_val is None or val > best_target_val:
                best_target_val = val

        # also add preference for staying mobile (avoid large obstacle adjacency)
        final_key = (-best_target_val, obstacle_pen(nx, ny), man(nx, ny, (w - 1) // 2, (h - 1) // 2), dx, dy)
        if best_move[0] is None or final_key < best_move[0]:
            best_move = (final_key, dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [best_move[1], best_move[2]]