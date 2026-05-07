def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    res = observation.get("resources", []) or []
    obst = observation.get("obstacles", []) or []
    obstacles = set(obst)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick best target: resource where we are not slower than opponent; closest first, then deterministic
    tx, ty = ox, oy
    best = None
    for rx, ry in res:
        sd = d(sx, sy, rx, ry)
        od = d(ox, oy, rx, ry)
        if sd <= od:
            key = (sd, -od, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
    if best is not None:
        tx, ty = best[1]

    if (sx, sy) == (tx, ty):
        return [0, 0]

    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = d(nx, ny, tx, ty)
        # minimize distance to target; tie-break deterministically
        key = (nd, nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, (dx, dy))

    if best_move is None:
        return [0, 0]
    return [best_move[1][0], best_move[1][1]]