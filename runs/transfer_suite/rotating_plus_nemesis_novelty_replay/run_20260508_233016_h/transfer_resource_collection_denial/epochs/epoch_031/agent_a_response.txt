def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    if (sx, sy) in set(tuple(p) for p in resources):
        return [0, 0]
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res = [tuple(r) for r in resources]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        chosen = None
        chosen_key = None
        for rx, ry in res:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Prefer being able to reach first, then fewer steps, then greater advantage vs opponent.
            key = (0 if myd <= opd else 1, myd, -(opd - myd), rx, ry)
            if chosen_key is None or key < chosen_key:
                chosen_key = key
                chosen = (rx, ry)

        rx, ry = chosen
        myd = man(nx, ny, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Maximize evaluation from this move.
        val = (0 if myd <= opd else 1, -myd, (opd - myd), -abs(nx - rx) - abs(ny - ry), nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]