def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def nearest(px, py):
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = md(px, py, rx, ry)
            if d < bestd:
                bestd = d
                best = (rx, ry)
        return best

    my_t = nearest(sx, sy)
    op_t = nearest(ox, oy)
    if my_t is None and op_t is None:
        return [0, 0]
    if op_t is None:
        target = my_t
    elif my_t is None:
        target = op_t
    else:
        if md(ox, oy, op_t[0], op_t[1]) <= md(sx, sy, my_t[0], my_t[1]):
            target = op_t
        else:
            target = my_t

    move_dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_score = -10**18

    tx, ty = target
    for dx, dy in move_dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        score = -myd + 0.01 * (opd - myd)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move