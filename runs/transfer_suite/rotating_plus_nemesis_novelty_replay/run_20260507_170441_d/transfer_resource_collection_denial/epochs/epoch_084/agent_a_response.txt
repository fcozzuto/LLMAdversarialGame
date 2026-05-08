def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obst.add((p[0], p[1]))

    def dist8(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    # Pick a "denial-aware" target: resources where we are much closer than the opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        lead = op_d - my_d  # positive => we are closer
        key = (-lead, my_d, (rx + 3 * ry) % 8)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Evaluate all possible moves and pick the one that improves our race to the target
    # while also keeping the opponent relatively far.
    best_m = None
    best_m_key = None
    any_ok = False
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        valid = ok(nx, ny)
        if valid:
            any_ok = True
        if not valid:
            continue
        any_ok = True
        my_to = dist8(nx, ny, tx, ty)
        op_to = dist8(ox, oy, tx, ty)
        # Prefer smaller distance to target; among ties, prefer larger opponent distance to target.
        # Extra penalty if move steps adjacent to obstacles to reduce getting stuck.
        adj_obst = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if (ex, ey) != (0, 0) and (nx + ex, ny + ey) in obst:
                    adj_obst += 1
        key = (my_to, -op_to, adj_obst, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is not None:
        return [best_m[0], best_m[1]]

    # If fully blocked, fall back to a deterministic direction that doesn't rely on obstacle avoidance.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]