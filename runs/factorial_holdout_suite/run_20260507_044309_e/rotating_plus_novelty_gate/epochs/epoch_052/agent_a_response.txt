def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    res = [tuple(r) for r in resources]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
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

    if not res:
        tx, ty = w // 2, h // 2
        best = min(valid, key=lambda m: (man(m[2], m[3], tx, ty), valid.index(m)))
        return [best[0], best[1]]

    res_set = set(res)
    # If we can grab immediately, do it deterministically.
    for dx, dy, nx, ny in valid:
        if (nx, ny) in res_set:
            return [dx, dy]

    best_move = None
    best_key = None
    # Heuristic: maximize advantage (reach earlier), with tie-break toward closer resources.
    for dx, dy, nx, ny in valid:
        best_adv = None
        for rx, ry in res:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Advantage score: smaller is better for our objective.
            # Strongly prefer resources we can reach no later than opponent.
            behind = myd - opd
            penalty = 10 * behind if behind > 0 else 0
            # Slight preference to nearer resources and to moves that reduce opponent reach.
            key = (penalty + myd - 0.6 * opd, myd + 0.1 * opd, valid.index((dx, dy, nx, ny)), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)

    if best_move is None:
        best = min(valid, key=lambda m: (man(m[2], m[3], ox, oy), valid.index(m)))
        return [best[0], best[1]]
    return [int(best_move[0]), int(best_move[1])]