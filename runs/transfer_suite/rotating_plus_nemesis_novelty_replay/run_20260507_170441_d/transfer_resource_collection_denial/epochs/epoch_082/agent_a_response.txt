def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def dist8(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    # Race target: resource where we are relatively closest (largest op-my lead).
    best_r = None
    best_r_key = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # positive => we are closer
        key = (-adv, my_d, rx, ry)
        if best_r_key is None or key < best_r_key:
            best_r_key = key
            best_r = (rx, ry)

    # Interception target: resource opponent is closest to (then we try to reduce their lead).
    best_i = None
    best_i_key = None
    for rx, ry in resources:
        op_d = dist8(ox, oy, rx, ry)
        my_d = dist8(sx, sy, rx, ry)
        key = (op_d, - (op_d - my_d), my_d, rx, ry)
        if best_i_key is None or key < best_i_key:
            best_i_key = key
            best_i = (rx, ry)

    tx, ty = best_r
    ix, iy = best_i

    # If opponent is clearly closer to their best resource, prioritize intercept target.
    my_to_i = dist8(sx, sy, ix, iy)
    op_to_i = dist8(ox, oy, ix, iy)
    target = (ix, iy) if op_to_i - my_to_i >= 2 else (tx, ty)
    tx, ty = target

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d = dist8(nx, ny, tx, ty)
        op_d = dist8(ox, oy, tx, ty)
        adv = op_d - my_d
        # Prefer larger adv', then closer to target, then smaller opponent distance, then deterministic.
        score = (-(adv), my_d, op_d, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    # Fallback: if all moves blocked, stay.
    return best_move if best_score is not None else [0, 0]