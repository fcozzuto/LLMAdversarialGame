def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        ax = a - c; ax = ax if ax >= 0 else -ax
        by = b - d; by = by if by >= 0 else -by
        return ax + by

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]
    if not resources:
        tx, ty = w // 2, h // 2
        best = min(valid, key=lambda m: (md(m[2], m[3], tx, ty), valid.index(m)))
        return [best[0], best[1]]

    res = [tuple(r) for r in resources]

    # Determine best move by considering one-step lookahead to a target resource.
    # Advantage = opponent_time - my_time (in Manhattan steps).
    best_move = None
    best_key = None
    for dx, dy, nx, ny in valid:
        chosen = None
        chosen_key = None
        for i, (rx, ry) in enumerate(res):
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # We want to capture earlier; otherwise, pick something that forces a better race.
            # Key: primary advantage, then smaller myd, then smaller opd, then deterministic tie on index.
            adv = opd - myd
            key = (adv, -myd, -opd, -i)
            if chosen_key is None or key > chosen_key:
                chosen_key = key
                chosen = (rx, ry, myd, opd)
        # If we can reach some resource at least as fast as opponent, strongly prefer those.
        my_best_myd, my_best_opd = chosen[2], chosen[3]
        prefer_fast = (my_best_myd <= my_best_opd)
        move_key = (1 if prefer_fast else 0, chosen_key, -md(nx, ny, ox, oy))
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]