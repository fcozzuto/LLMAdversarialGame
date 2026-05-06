def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Predict opponent's likely target: closest resource to opponent (deterministic tie-break).
    pred = None
    pred_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = man(ox, oy, rx, ry)
        key = (d, rx, ry)
        if pred_key is None or key < pred_key:
            pred_key = key
            pred = (rx, ry)

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # Choose action target:
    # 1) If we can beat predicted target, go for it.
    # 2) Otherwise, pick any resource where our tempo advantage is best.
    # 3) Fall back to moving toward center.
    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        tempo = oppd - myd  # positive means we arrive earlier
        center_pref = -(abs(rx - cx) + abs(ry - cy))
        # If this is predicted target, strongly prioritize contesting it.
        is_pred = 1 if pred == (rx, ry) else 0
        # Key: primarily maximize tempo, then prefer center, then determinism.
        key = (-tempo, -is_pred, -center_pref, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if pred is not None:
        rx, ry = pred
        if (rx, ry) not in obstacles and man(sx, sy, rx, ry) <= man(ox, oy, rx, ry):
            best_target = pred

    if not best_target:
        best_target = (cx, cy)

    tx, ty = best_target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Avoid stepping into obstacles when possible by reducing move components.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try axis moves deterministically; if both blocked, stay.
        cand = [(dx, 0), (0, dy), (dx, dy)]
        for adx, ady in cand:
            tx2, ty2 = sx + adx, sy + ady
            if 0 <= tx2 < w and 0 <= ty2 < h and (tx2, ty2) not in obstacles:
                dx, dy = adx, ady
                break
        else:
            dx, dy = 0, 0

    # Ensure within bounds (engine would otherwise keep position, but keep deterministic).
    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w and 0 <= ny < h):
        if 0 <= sx + dx < w:
            dx = 0
        else:
            dy = 0
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            dx, dy = 0, 0

    return [int(dx), int(dy)]