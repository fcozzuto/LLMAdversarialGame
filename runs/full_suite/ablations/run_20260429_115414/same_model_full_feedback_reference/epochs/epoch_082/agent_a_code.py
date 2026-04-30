def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
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

    def kdist(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if resources:
        best_r = resources[0]
        best_key = (-10**18, -10**18)
        for rx, ry in resources:
            ds = kdist(sx, sy, rx, ry)
            do = kdist(ox, oy, rx, ry)
            adv = do - ds
            # Prefer resources we can reach sooner; tie-break by closer to us.
            key = (adv, -ds)
            if key > best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (W - 1) // 2, (H - 1) // 2

    # If we can grab a resource immediately, do it.
    for dx, dy, nx, ny in legal:
        if (nx, ny) in set(resources):
            return [dx, dy]

    # Otherwise, pick move that reduces our distance to target and slightly increases opponent distance to it.
    best = None
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        ds = kdist(nx, ny, tx, ty)
        do = kdist(ox, oy, tx, ty)
        # Opponent distance doesn't change this turn; still include a small penalty for far moves.
        val = (-(ds) * 20) + (do * 0) - (abs(dx) + abs(dy)) * 0.1 - (kdist(nx, ny, sx, sy) * 0.01)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]