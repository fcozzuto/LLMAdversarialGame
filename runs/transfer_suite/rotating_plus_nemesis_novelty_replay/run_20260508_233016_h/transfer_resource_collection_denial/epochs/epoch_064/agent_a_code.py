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

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        secure = my_d < op_d
        # Prefer resources we can reach earlier; otherwise prefer delaying/denying (op advantage small).
        key = (0 if secure else 1, my_d if secure else op_d - my_d, op_d if secure else my_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    # If our target is still likely uncontested, add a small "intercept" bias toward routes that reduce op distance to it.
    my_d0 = dist(sx, sy, tx, ty)
    op_d0 = dist(ox, oy, tx, ty)
    target_contested = 1 if my_d0 >= op_d0 else 0

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_dt = dist(nx, ny, tx, ty)
        op_dt = dist(ox, oy, tx, ty)
        my_do = dist(nx, ny, ox, oy)
        # Primary: get closer to target; Secondary: if contested, keep opponent farther from it (via increasing our distance to them).
        k = (
            my_dt,
            my_dt - my_d0,
            target_contested * (-my_do),
            dist(nx, ny, resources[0][0], resources[0][1]),
            nx,
            ny,
        )
        if best_move_key is None or k < best_move_key:
            best_move_key = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]