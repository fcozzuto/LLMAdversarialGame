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
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose best target by advantage: opponent delay vs us (prefer we arrive sooner)
    best = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d
        key = (-adv, my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), adv)

    _, (tx, ty), _ = best

    # Score candidate moves by resulting advantage and distance to target
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = dist8(nx, ny, tx, ty)

        # Secondary: if opponent could snatch nearer, prevent it by also minimizing their closeness to target
        op_d = dist8(ox, oy, tx, ty)

        # Primary advantage after our move: larger means we are closer relative to opponent (more denial)
        adv = op_d - my_d
        # If we are equally advantaged, reduce our distance; tie-break deterministically
        cand = (-adv, my_d, nx, ny)
        if best_move is None or cand < best_move[0]:
            best_move = (cand, (dx, dy))

    if best_move is None:
        return [0, 0]
    dx, dy = best_move[1]
    return [dx, dy]