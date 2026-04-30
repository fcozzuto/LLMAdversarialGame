def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    # Determine a target resource: prefer ones where we are strictly closer than opponent.
    best = None
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        advantage = d2 - d1  # higher is better (we closer)
        key = (advantage, -d1, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry), d1, d2)

    # If no resources, just stay; otherwise move to minimize our distance to the chosen target,
    # but break ties by also reducing opponent's distance (interference).
    if best is None:
        return [0, 0]
    (advkey, (tx, ty), d1, d2) = best

    best_move = None
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # primary: our distance; secondary: advantage after move; tertiary: deterministic order
        myd_key = myd
        new_adv = opd - myd  # higher better
        k = (-myd_key, new_adv, dx, dy)
        if best_move is None or k > best_move[0]:
            best_move = (k, (dx, dy))
    return [int(best_move[1][0]), int(best_move[1][1])]