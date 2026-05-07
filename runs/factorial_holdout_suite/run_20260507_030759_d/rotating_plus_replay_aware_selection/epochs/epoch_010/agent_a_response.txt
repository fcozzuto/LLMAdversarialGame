def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    res_set = set(tuple(p) for p in resources)
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
        key = (od - sd, -abs(ry - sy), -abs(rx - sx), -sd, -(rx + ry))
        if best_key is None or key > best_key:
            best_key, best_cell = key, (rx, ry)

    tx, ty = best_cell
    best_move = [0, 0]
    best_move_key = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        collect = 1 if (nx, ny) in res_set else 0
        key = (collect, (nod - nsd), -nsd, -abs(ny - ty), -abs(nx - tx), -abs(ny - sy), -abs(nx - sx))
        if best_move_key is None or key > best_move_key:
            best_move_key, best_move = key, [mx, my]
    return best_move