def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (0 if ds <= do else 1, ds, do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    best_move = (0, 0)
    best_key2 = None
    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]
    do0 = cheb(ox, oy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ds1 = cheb(nx, ny, tx, ty)
        do1 = cheb(ox, oy, tx, ty)
        key2 = (0 if ds1 <= do1 else 1, ds1, -do1, dx == 0 and dy == 0, nx, ny)
        if best_key2 is None or key2 < best_key2:
            best_key2 = key2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]