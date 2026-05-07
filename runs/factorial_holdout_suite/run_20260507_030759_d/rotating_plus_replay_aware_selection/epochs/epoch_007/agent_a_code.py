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

    best_cell = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Keep a strong advantage bias; additionally prefer resources that align better with our row
        # (opponent sweep behavior tends to overcommit along rows).
        row_align = -abs(ry - sy)
        col_align = -abs(rx - sx)
        key = (od - sd, row_align, col_align, -sd, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (rx, ry)

    tx, ty = best_cell
    best = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        cand = (d, mx, my)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[1], best[2]]