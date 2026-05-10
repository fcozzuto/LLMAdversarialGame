def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        if my_d < op_d:
            key = (0, my_d, op_d, rx, ry)
        else:
            key = (1, -(op_d - my_d), op_d, my_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    best_move = [0, 0]
    best_eval = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my2 = dist(nx, ny, tx, ty)
        op2 = dist(ox, oy, tx, ty)
        adv = op2 - my2  # positive means we're closer than opponent to the target
        # Prefer moves that keep/restore "secure" pressure; then reduce our distance.
        mode = 0 if my2 < op2 else 1
        # Deterministic tie-break by dx,dy ordering.
        eval_key = (mode, -adv, my2, dx, dy)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = [dx, dy]

    return best_move if best_eval is not None else [0, 0]