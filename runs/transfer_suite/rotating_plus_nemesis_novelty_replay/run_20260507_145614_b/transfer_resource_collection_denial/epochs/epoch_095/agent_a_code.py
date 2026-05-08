def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    best = -10**18
    best_move = [0, 0]

    # pick target resource deterministically for tie-breaking: min (dist, x, y)
    for dx0, dy0 in dirs:
        nx, ny = sx + dx0, sy + dy0
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        score = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Higher when we are closer than opponent
            # If ds==do, prefer resources that are closer overall and earlier in deterministic ordering
            score += (do - ds) * 10 - ds
            if ds == 0 and do > 0:
                score += 500  # immediate collection

        # small preference to move toward the most contested/nearest resource
        # deterministically choose one target for tie-break
        tx, ty = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
        score += -cheb(nx, ny, tx, ty)

        if score > best:
            best = score
            best_move = [dx0, dy0]
        elif score == best:
            # tie-break: lexicographic dx then dy for determinism
            if [dx0, dy0] < best_move:
                best_move = [dx0, dy0]

    return [int(best_move[0]), int(best_move[1])]