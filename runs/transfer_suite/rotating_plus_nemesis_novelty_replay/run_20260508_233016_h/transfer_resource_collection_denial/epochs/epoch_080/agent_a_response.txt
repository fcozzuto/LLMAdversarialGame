def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        if my_d < op_d:
            key = (0, my_d, op_d, rx, ry)
        else:
            key = (1, -(op_d - my_d), my_d, op_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    my_d0 = dist(sx, sy, tx, ty)
    op_d0 = dist(ox, oy, tx, ty)
    secure = my_d0 < op_d0

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_next = dist(nx, ny, tx, ty)
        if my_next == 0:
            sc = (1000000, -op_d0, 0)
        elif secure:
            sc = (0, -my_next, op_d0 - my_next)
        else:
            sc = (0, op_d0 - my_next, -my_next)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    dx, dy = best_mv
    if not (-1 <= dx <= 1 and -1 <= dy <= 1):
        return [0, 0]
    return [int(dx), int(dy)]