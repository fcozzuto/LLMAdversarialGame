def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, -nx, -ny)
            if best_val is None or key < best_val:
                best_val = key
                best = [dx, dy]
        return best

    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        key = (-adv, do, rx, ry)  # maximize adv, then minimize opponent distance, then deterministic
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res if best_res is not None else (w // 2, h // 2)

    cur_ds = cheb(sx, sy, rx, ry)
    cur_do = cheb(ox, oy, rx, ry)
    prefer = (cur_do - cur_ds) >= 0  # if we can already win this target, focus even more on keeping advantage

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds2 = cheb(nx, ny, rx, ry)

        # Estimate opponent next distance if they chase the same target
        do_now = cheb(ox, oy, rx, ry)
        do2 = do_now - 1 if do_now > 0 else 0  # optimistic but bounded, deterministic

        adv2 = do2 - ds2
        # If currently winning, prioritize higher advantage strongly; else race by minimizing our distance, while reducing opponent lead.
        if prefer:
            score = (-adv2, ds2, rx, ry, dx, dy)
        else:
            score = (-adv2, ds2, do2, rx, ry, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move