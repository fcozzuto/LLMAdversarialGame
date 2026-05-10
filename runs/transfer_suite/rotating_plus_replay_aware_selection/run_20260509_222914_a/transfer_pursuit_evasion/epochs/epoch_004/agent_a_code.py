def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            res.append((p[0], p[1]))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if res:
            dmin = None
            for rx, ry in res:
                d = man(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
            val = -dmin + 0.3 * man(nx, ny, ox, oy)
        else:
            val = man(nx, ny, ox, oy)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    nx, ny = x + dx, y + dy
    if not in_bounds(nx, ny):
        return [0, 0]
    return [dx, dy]