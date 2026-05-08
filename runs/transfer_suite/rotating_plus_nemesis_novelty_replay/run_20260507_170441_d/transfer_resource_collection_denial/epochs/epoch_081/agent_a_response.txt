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

    if not resources:
        return [0, 0]

    def dist8(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # Pick best resource to race: maximize lead (opponent_distance - my_distance), tie-break by my_distance, then coords.
    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d
        key = (-adv, my_d, rx, ry)  # smallest key => best
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    cur_my = dist8(sx, sy, tx, ty)
    op_to_t = dist8(ox, oy, tx, ty)

    # Choose move that maximizes resulting lead; if tied, prefer shorter to target; then deterministic move ordering.
    best_move = [0, 0]
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        lead_after = op_to_t - nd
        lead_before = op_to_t - cur_my
        delta_lead = lead_after - lead_before
        mkey = (-delta_lead, nd, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    return best_move