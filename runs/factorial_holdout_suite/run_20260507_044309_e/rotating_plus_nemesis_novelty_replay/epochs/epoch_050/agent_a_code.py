def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    res = observation.get("resources") or []
    if not res:
        return [0, 0]

    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick best target under "resource_denier": prefer resources we can secure earlier than opponent.
    best_targets = []
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # higher is better
        best_targets.append((adv, -ds, -rx, -ry, rx, ry))
    if not best_targets:
        return [0, 0]
    best_targets.sort(reverse=True)
    top = best_targets[:3]  # small, deterministic

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate this move by how good it makes us vs opponent on the best remaining targets.
        # Add slight bias toward reducing distance to avoid stalling.
        cur_best = None
        for adv, nds, nrx, nry, rx, ry in top:
            ds2 = cheb(nx, ny, rx, ry)
            do2 = cheb(ox, oy, rx, ry)
            val = (do2 - ds2) - 0.05 * ds2
            if cur_best is None or (val, -ds2, rx, ry) > cur_best:
                cur_best = (val, -ds2, rx, ry)
        if cur_best is None:
            continue
        val, negds2, rx, ry = cur_best
        cand = (val, negds2, dx, dy)  # deterministic tie-break
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]