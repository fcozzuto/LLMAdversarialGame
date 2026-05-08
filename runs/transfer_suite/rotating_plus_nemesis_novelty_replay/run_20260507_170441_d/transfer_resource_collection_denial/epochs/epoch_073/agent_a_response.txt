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
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a tactical target: prefer resources where we can catch up (or at least contest).
    best_target = resources[0]
    best_tkey = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        # adv > 0 means we are closer
        adv = my_d - op_d
        # For contesting: prioritize small |adv| (fight), then smaller my_d.
        row_contest = 1 if ry == oy else 0
        col_contest = 1 if rx == ox else 0
        tkey = (abs(adv), my_d, -(row_contest + col_contest), rx, ry)  # deterministic
        if best_tkey is None or tkey < best_tkey:
            best_tkey = tkey
            best_target = (rx, ry)

    tx, ty = best_target
    base_op_d = dist8(ox, oy, tx, ty)

    # If we're globally behind, shift to a reachable "closest contested" resource.
    # Use remaining_resource_count as a rough proxy for how aggressively we should race.
    behind = True
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        if my_d <= op_d:
            behind = False
            break

    # Evaluate each move with a simple one-step advantage forecast plus blocking bias.
    best_move = [0, 0]
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        # Favor making (our distance) <= (op distance) soon; also reduce our distance.
        adv_after = nd - base_op_d  # smaller is better
        chase = nd
        # Blocking bias: if opponent is sweeping rows, moving to your diagonal approach toward their row is useful.
        block_bias = -1 if ny == oy else 0
        # If behind, prefer moves that minimize our distance to the nearest resource overall, but avoid empty wandering.
        if behind and observation.get("remaining_resource_count", len(resources)) <= 6:
            near_my = min(dist8(nx, ny, rx, ry) for rx, ry in resources)
            chase = near_my
        mkey = (adv_after, chase, -(abs(nx - ox) + abs(ny - oy)), nx, ny)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    return best_move