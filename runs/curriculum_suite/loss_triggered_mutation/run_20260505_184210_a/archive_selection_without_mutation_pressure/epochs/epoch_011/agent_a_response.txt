def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, cx, cy)
            key = (d, dx, dy, observation.get("turn_index", 0) % 2)
            if best is None or key < best:
                best = key
        return [best[1], best[2]]

    best_key = None
    ti = observation.get("turn_index", 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        best_adv = None
        best_ds = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => we are closer than opponent
            if best_adv is None or (adv, -do, -ds, rx, ry) > (best_adv, best_do, best_ds2, best_rx, best_ry):
                best_adv, best_do, best_ds2, best_rx, best_ry = adv, do, ds, rx, ry
            if best_ds is None or (ds, rx, ry) < (best_ds, best_rxx, best_ryy):
                best_ds, best_rxx, best_ryy = ds, rx, ry

        target_ds = best_ds if best_adv is None else cheb(nx, ny, best_rx, best_ry)
        target_do = best_do if best_adv is None else best_do

        # Prefer moves that create advantage; otherwise push to the closest safe target.
        # Add a small deterministic tie-break to avoid repeating patterns against row sweep.
        adv_score = best_adv if best_adv is not None else -10**9
        key = (-adv_score, target_ds, -target_do, (nx + ny + ti) % 3, dx, dy)
        if best_key is None or key < best_key:
            best_key = key

    return [best_key[4], best_key[5]]