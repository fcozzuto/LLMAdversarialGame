def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        chosen_key = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we are closer to; if tied, prefer smaller sd; also slightly reward larger od.
            key = (od - sd, -sd, od, -man(nx, ny, ox, oy))
            if chosen_key is None or key > chosen_key:
                chosen_key = key

        if chosen_key is None:
            continue

        # Secondary tie-breakers across moves: closer to the currently best target, then lexicographic on move.
        move_key = (chosen_key[0], chosen_key[1], chosen_key[2], chosen_key[3], -dx, -dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = [dx, dy]

    return best_move