def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mx, my in cand:
            if valid(sx + mx, sy + my):
                return [mx, my]
        return [0, 0]

    occupied = (sx, sy)
    if any((rx == occupied[0] and ry == occupied[1]) for rx, ry in resources):
        return [0, 0]

    best = None
    best_move = (0, 0)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Prefer resources we can reach sooner than opponent; if none, go for closest anyway.
        keys_good = []
        keys_all = []
        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            op_d = man(ox, oy, rx, ry)
            rel = my_d - op_d
            keys_all.append((rel, my_d, rx, ry))
            if my_d < op_d:
                keys_good.append((rel, my_d, rx, ry))

        if keys_good:
            key = min(keys_good)[:2]
        else:
            key = min(keys_all)[:2]

        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]