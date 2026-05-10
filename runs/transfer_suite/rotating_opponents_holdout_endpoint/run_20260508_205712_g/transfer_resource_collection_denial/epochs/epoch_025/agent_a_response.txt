def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick best target by "contest swing" but also avoid far targets too late-game
    turns = observation.get("turns_remaining", 1)
    time_weight = 1.0 if turns > 10 else (turns / 10.0)
    best_tx, best_ty = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        swing = opd - myd  # positive => closer than opponent
        # Prefer reasonably reachable resources, and slightly prefer those not at edges (less escape volatility)
        reach_bias = -myd * (0.6 + 0.4 * time_weight)
        edge_pen = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)) * 0.05
        key = (swing, reach_bias, edge_pen)
        if best_key is None or key > best_key:
            best_key = key
            best_tx, best_ty = rx, ry

    # Move scoring: maximize immediate swing, but penalize getting adjacent to obstacles
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def obst_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    p += 1
        return p

    best_delta = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        myd2 = man(nx, ny, best_tx, best_ty)
        opd2 = man(ox, oy, best_tx, best_ty)

        # Also consider moving toward a safer position if opponent isn't contesting
        swing = opd2 - myd2
        myd_cur = man(sx, sy, best_tx, best_ty)
        closer = myd_cur - myd2  # positive => improvement
        val = (swing, closer, -myd2, -(obst_pen(nx, ny)))
        if best_val is None or val > best_val:
            best_val = val
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]