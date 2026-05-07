def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources_raw = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    resources = []
    for p in resources_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        da = a - c
        if da < 0:
            da = -da
        db = b - d
        if db < 0:
            db = -db
        return da + db

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves.sort(key=lambda d: (d[0], d[1]))

    best_dxdy = [0, 0]
    best_adv = -10**9
    best_ds = 10**9
    best_tx_ty = (10**9, 10**9)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_for_move_adv = -10**9
        best_for_move_ds = 10**9
        best_for_move_target = (10**9, 10**9)

        for tx, ty in resources:
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            adv = do - ds  # positive means we reach earlier (or they later)
            if adv > best_for_move_adv or (adv == best_for_move_adv and (ds < best_for_move_ds or (ds == best_for_move_ds and (tx, ty) < best_for_move_target))):
                best_for_move_adv = adv
                best_for_move_ds = ds
                best_for_move_target = (tx, ty)

        if best_for_move_adv > best_adv or (best_for_move_adv == best_adv and (best_for_move_ds < best_ds or (best_for_move_ds == best_ds and best_for_move_target < best_tx_ty))):
            best_adv = best_for_move_adv
            best_ds = best_for_move_ds
            best_tx_ty = best_for_move_target
            best_dxdy = [dx, dy]

    return best_dxdy