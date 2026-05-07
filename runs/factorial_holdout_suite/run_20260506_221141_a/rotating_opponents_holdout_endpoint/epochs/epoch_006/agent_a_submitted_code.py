def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(observation.get("obstacles") or [])
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_value_from(x, y):
        best = None
        for rx, ry in resources:
            myd = abs(x - rx) + abs(y - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            v = myd - 0.5 * opd
            if best is None or v < best:
                best = v
        return best

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = best_value_from(nx, ny)
        if best_val is None or v < best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move