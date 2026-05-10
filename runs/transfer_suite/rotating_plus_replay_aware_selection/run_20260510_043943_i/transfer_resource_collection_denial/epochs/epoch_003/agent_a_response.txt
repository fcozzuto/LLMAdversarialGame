def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    target = None
    if resources:
        best_key = None
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            key = (sd - 1.2 * od, sd, -rx, -ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        target = best if best is not None else None

    if target is None:
        target = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = target
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = dist((nx, ny), (tx, ty))
        nod = dist((nx, ny), (ox, oy))
        val = (nsd, -nod, abs(dx) + abs(dy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    if best_move is None:
        best_move = (0, 0)
    return [int(best_move[0]), int(best_move[1])]