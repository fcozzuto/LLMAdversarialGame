def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx + dy

    # Pick a resource we can potentially secure: prioritize closer than opponent, then overall closeness.
    best = None
    best_key = None
    for r in resources:
        if r in obstacles:
            continue
        myd = dist((sx, sy), r)
        opd = dist((ox, oy), r)
        # Key: we prefer resources where we are not much farther than opponent, then closer to us, then tie-break by coords.
        key = (opd - myd, -myd, -r[0], -r[1])  # higher better on first two; smaller coords via negatives
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best if best is not None else (sx, sy)

    # Compute candidate deltas toward target (including stay).
    def step_toward(tx, ty):
        dx = 0
        dy = 0
        if tx > sx: dx = 1
        elif tx < sx: dx = -1
        if ty > sy: dy = 1
        elif ty < sy: dy = -1
        return dx, dy

    desired = step_toward(tx, ty)

    candidates = []
    # Ordered: desired diagonal/axis, then alternative moves by closeness to target, then stay.
    candidates.append(desired)
    alt = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    seen = set([desired])
    for d in alt:
        if d not in seen:
            candidates.append(d)
            seen.add(d)

    def valid(d):
        dx, dy = d
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    # If opponent is closer to the chosen target and we're not, try to intercept by moving to a neighbor that reduces our distance to opponent.
    chosen_myd = dist((sx, sy), (tx, ty)) if best is not None else 0
    chosen_opd = dist((ox, oy), (tx, ty)) if best is not None else 0
    intercept_mode = best is not None and chosen_myd > chosen_opd

    best_move = (0, 0)
    best_val = None
    for d in candidates:
        if not valid(d):
            continue
        nx, ny = sx + d[0], sy + d[1]
        # Evaluate: progress to target; optionally also reduce opponent distance (intercept).
        my_to_t = dist((nx, ny), (tx, ty)) if best is not None else 0
        my_to_o = dist((nx, ny), (ox, oy))
        key = None
        if intercept_mode:
            # prioritize decreasing our distance to opponent while not getting too far from target
            key = (-my_to_o, -my_to_t, -nx, -ny)
        else:
            key = (-my_to_t, -my_to_o, -nx, -ny)
        if best_val is None or key > best_val:
            best_val = key
            best_move = d

    return [int(best_move[0]), int(best_move[1])]