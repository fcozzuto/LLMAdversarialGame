def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # king distance

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # bigger => we are earlier
        key = (-adv, my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), adv, my_d)
    (_, (tx, ty), adv, my_d) = best

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    preferred = (0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1))
    px, py = sx + preferred[0], sy + preferred[1]
    if preferred != (0, 0) and ok(px, py):
        return [preferred[0], preferred[1]]

    curd = dist8(sx, sy, tx, ty)
    best_step = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        # minimize distance to target; then maximize advantage margin; deterministic by move order
        step_key = (nd, -((dist8(ox, oy, tx, ty) - nd)), nx, ny)
        if best_step is None or step_key < best_step[0]:
            best_step = (step_key, (dx, dy))
    if best_step is None:
        return [0, 0]
    return [best_step[1][0], best_step[1][1]]