def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = obstacles_list if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = None
    best_key = None

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose the best resource from the next position; maximize lead over opponent.
        local_best = None
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # Primary: opponent lead after we move (positive is good for us)
            # Secondary: sooner capture by us, then nearer/lexicographic.
            key = (do - ds, -ds, -rx, -ry)
            if local_best is None or key > local_best[0]:
                local_best = (key, (rx, ry), ds, do)

        if local_best is None:
            continue

        (lead_key, (tx, ty), ds, do) = local_best
        # Prefer moves that keep lead positive; otherwise minimize our distance and reduce opponent threat.
        move_key = (lead_key[0], -lead_key[1], -do + ds, abs(tx - nx) + abs(ty - ny), dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]