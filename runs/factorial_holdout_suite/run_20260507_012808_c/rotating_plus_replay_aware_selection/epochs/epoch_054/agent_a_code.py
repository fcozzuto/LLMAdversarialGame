def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    res = [tuple(r) for r in resources]

    best = None
    best_key = (-10**18, -10**18, -10**18, -10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_adv = -10**18
        best_neg_ds = 10**18
        win_cnt = 0
        close_opp = 10**18

        for rx, ry in res:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds  # positive if we can arrive no later than opponent by more than 0
            if adv > best_adv:
                best_adv = adv
            if ds < best_neg_ds:
                best_neg_ds = ds
            if adv > 0:
                win_cnt += 1
            if do < close_opp:
                close_opp = do

        # Prefer moves that secure resources earlier; then go for closer resources; then reduce opponent's access.
        key = (best_adv, win_cnt, -best_neg_ds, -close_opp)
        if key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]