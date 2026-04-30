def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set(map(tuple, obstacles_raw))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        dp = cheb(ox, oy, rx, ry)
        key = (ds - dp, ds)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        best_r = tuple(map(int, resources[0]))

    tx, ty = best_r
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ds_next = cheb(nx, ny, tx, ty)
        dp_cur = cheb(ox, oy, tx, ty)
        move_key = (ds_next - dp_cur, ds_next, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_move_key is None or move_key < best_move_key:
            best_move_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]