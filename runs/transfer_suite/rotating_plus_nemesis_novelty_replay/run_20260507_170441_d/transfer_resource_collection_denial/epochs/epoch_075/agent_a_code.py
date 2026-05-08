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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    # Pick a target resource:
    # - If opponent can reach it no later than us, treat as contested and prioritize the one we can secure fastest.
    # - Otherwise, prioritize the one where we have the biggest time advantage.
    my_best_adv = None
    contested_best = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        if op_d <= my_d:
            # contested: smaller my_d is better; tie-break by larger margin opponent still wins late (smaller op_d-my_d)
            key = (my_d, op_d, rx, ry)
            if contested_best is None or key < contested_best[0]:
                contested_best = (key, (rx, ry), my_d, op_d)
        else:
            adv = my_d - op_d  # positive means we are later; negative means we are earlier
            # want smallest my_d and also strong lead (op_d - my_d large)
            key = (-(op_d - my_d), my_d, rx, ry)
            if my_best_adv is None or key < my_best_adv[0]:
                my_best_adv = (key, (rx, ry), my_d, op_d)

    if contested_best is not None:
        (tx, ty) = contested_best[1]
    else:
        (tx, ty) = my_best_adv[1]

    # Choose move that maximizes our winning likelihood for the target and also reduces opponent progress.
    target_op_d = dist8(ox, oy, tx, ty)
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        # Higher is better:
        # - Prefer minimizing our distance to the target
        # - Prefer increasing the time gap vs opponent to the same target
        gap = target_op_d - nd
        # Small tie-break: also reduce distance to nearest other resource to avoid dead-ends
        md_other = 999
        for rx, ry in resources:
            dd = dist8(nx, ny, rx, ry)
            if dd < md_other:
                md_other = dd
        key = (-gap, nd, md_other, rx if False else 0)  # deterministic without extra vars
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return best_move