def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Compute advantage to each resource; prefer resources where we beat opponent (adv >= 0)
        adv_best = -10**9
        ds_best = 10**9
        do_best = -10**9
        adv_nonneg_best = -10**9
        ds_nonneg_best = 10**9
        do_nonneg_best = -10**9

        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds

            if adv >= 0:
                if adv > adv_nonneg_best or (adv == adv_nonneg_best and (ds < ds_nonneg_best or (ds == ds_nonneg_best and do > do_nonneg_best))):
                    adv_nonneg_best, ds_nonneg_best, do_nonneg_best = adv, ds, do

            if adv > adv_best or (adv == adv_best and (ds < ds_best or (ds == ds_best and do > do_best))):
                adv_best, ds_best, do_best = adv, ds, do

        if adv_nonneg_best >= 0:
            key = (1, adv_nonneg_best, -ds_nonneg_best, do_nonneg_best)
        else:
            key = (0, adv_best, -ds_best, do_best)

        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move