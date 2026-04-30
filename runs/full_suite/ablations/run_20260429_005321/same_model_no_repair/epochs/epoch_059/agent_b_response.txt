def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))  # Chebyshev for 8-dir moves

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def safe_neighbors(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    if not resources:
        return [0, 0]

    # Choose a target: prefer resources where we are closer than opponent; otherwise prefer "less bad" targets.
    best_t = None
    best_t_val = -10**18
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        myd = dist(sx, sy, tx, ty)
        opd = dist(ox, oy, tx, ty)
        # If we are closer: strongly prefer; if not: still consider but less.
        rel = opd - myd
        center = -0.06 * (abs(tx - cx) + abs(ty - cy))
        # Small penalty for being near obstacles (reduce trapping)
        near_obs = min(myd, opd)
        obs_pen = 0.15 * ((min(abs(tx - ax) + abs(ty - ay) for ax, ay in obstacles) if obstacles else 99) <= 1) if obstacles else 0
        val = 3.2 * rel - 0.55 * myd + center - obs_pen
        if val > best_t_val:
            best_t_val = val
            best_t = (tx, ty)

    tx, ty = best_t
    # Evaluate next move by resulting distance to target and mobility.
    best_move = (0, 0)
    best_move_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        if safe_neighbors(nx, ny) <= 1 and (nx, ny) != (tx, ty):
            continue  # avoid getting trapped unless we can collect
        myd2 = dist(nx, ny, tx, ty)
        opd2 = dist(ox, oy, tx, ty)
        rel2 = opd2 - myd2
        # Prefer moves that improve our relative position and keep away from edges a bit.
        edge_pen = 0.05 * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
        val = 3.0 * rel2 - 0.8 * myd2 + edge_pen
        if val > best_move_val:
            best_move_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]