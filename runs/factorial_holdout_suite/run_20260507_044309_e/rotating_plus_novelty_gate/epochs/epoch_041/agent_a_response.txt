def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy

    resources = observation.get("resources", []) or []
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None; bd = 10**9; bi = 10**9
        for i, (dx, dy, nx, ny) in enumerate(valid):
            d = dist(nx, ny, tx, ty)
            if d < bd or (d == bd and i < bi):
                bd = d; bi = i; best = (dx, dy)
        return [best[0], best[1]]

    # Predict opponent's nearest resource; then try to be earlier (intercept race).
    opp_best = None; opp_bd = 10**9; opp_i = 10**9
    for i, (rx, ry) in enumerate(resources):
        d = dist(ox, oy, rx, ry)
        if d < opp_bd or (d == opp_bd and i < opp_i):
            opp_bd = d; opp_i = i; opp_best = (rx, ry)

    # Choose move by maximizing guaranteed/competitive advantage toward the opponent's likely target,
    # with fallback to any resource where we are closer.
    best_move = None; best_val = -10**18; best_i = 10**18
    for i, (dx, dy, nx, ny) in enumerate(valid):
        my_d_to_pred = dist(nx, ny, opp_best[0], opp_best[1])
        opp_d_pred = opp_bd
        # Advantage: negative means we are closer than opponent (good).
        val = -(my_d_to_pred - opp_d_pred)
        # If we can't beat pred, look for any resource we can reach earlier than opponent.
        for j, (rx, ry) in enumerate(resources):
            md = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer earlier arrivals strongly; otherwise mild focus on nearer items.
            advantage = od - md
            if advantage > 0:
                val = 1000 + advantage * 10 - md
            else:
                if val < (100 + od - md) - md * 0.1:
                    val = (100 + od - md) - md * 0.1
        if val > best_val or (val == best_val and i < best_i):
            best_val = val; best_i = i; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]