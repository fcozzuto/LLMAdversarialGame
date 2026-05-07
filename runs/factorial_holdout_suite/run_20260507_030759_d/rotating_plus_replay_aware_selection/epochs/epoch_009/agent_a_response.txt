def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_cell = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -abs(ry - sy), -abs(rx - sx), -sd, -(rx + ry), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (rx, ry)

    tx, ty = best_cell
    best_move = (0, 0)
    best_move_key = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Prefer reducing our distance to target, while keeping us ahead of opponent
        # and slightly favoring closer-to-middle progress to avoid dead-end patterns.
        midx = (w - 1) // 2
        midy = (h - 1) // 2
        key = (nod - nsd, -nsd, -abs(ny - midy), -abs(nx - midx), -(mx * 0 + my), -(nx + ny))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]