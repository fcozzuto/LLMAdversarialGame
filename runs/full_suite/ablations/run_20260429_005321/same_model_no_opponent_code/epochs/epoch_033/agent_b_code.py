def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def dist_to_target(nx, ny, tx, ty):
        return cheb(nx, ny, tx, ty)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = int(x) + dx, int(y) + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Drift away from opponent a bit if no resources visible
        best = None
        best_key = None
        for dx, dy, nx, ny in legal:
            myd = cheb(nx, ny, ox, oy)
            key = (myd, -nx, -ny, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target: prioritize resources where we are closer than opponent, then reduce my distance.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_target = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(x, y, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Advantage first, then prefer closer and more central targets, deterministic tie-break.
        center_bias = -abs(rx - cx) - abs(ry - cy)
        key = (opd - myd, -myd, center_bias, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Next move: minimize my distance to target; if tied, maximize opponent distance; penalize stepping near obstacles indirectly via illegality already.
    best = None
    best_key = None
    for dx, dy, nx, ny in legal:
        myd2 = dist_to_target(nx, ny, tx, ty)
        opd2 = dist_to_target(nx, ny, ox, oy)
        step_center = -abs(nx - cx) - abs(ny - cy)
        key = (-myd2, opd2, step_center, -nx, -ny, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]