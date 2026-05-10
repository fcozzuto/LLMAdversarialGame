def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_r = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        val = (od - sd) * 1000 - sd
        val += ((sd + rx + ry) & 1) * 2
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r
    cur_sd = man(sx, sy, tx, ty)
    cur_od = man(ox, oy, tx, ty)

    best_move = [0, 0]
    best_move_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)  # opponent position unchanged this turn
        move_val = (cur_sd - sd) * 2000 - sd
        move_val += (od - cur_od) * 5  # usually 0, but keeps structure deterministic
        move_val += ((nx + ny + tx + ty) & 1) * 1
        if move_val > best_move_val:
            best_move_val = move_val
            best_move = [nx - sx, ny - sy]

    return best_move