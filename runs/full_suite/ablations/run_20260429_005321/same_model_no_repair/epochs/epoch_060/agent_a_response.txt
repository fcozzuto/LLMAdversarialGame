def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    center_pen = 0.04

    # Pick best target by "who's closer" and centrality; avoid obstacle cells.
    best_t = None
    best_score = -10**18
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        rel = opd - myd  # positive => we're closer
        dist_center = abs(tx - cx) + abs(ty - cy)
        score = 2.2 * rel - center_pen * dist_center
        # Slight bias to nearer targets when contest is even
        score -= 0.06 * myd
        if score > best_score:
            best_score = score
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t

    # Evaluate moves: prefer improving our distance to target relative to opponent.
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd1 = cheb(nx, ny, tx, ty)
        opd1 = cheb(ox, oy, tx, ty)

        # If we can get significantly closer than opponent, prioritize.
        v = 3.0 * (opd1 - myd1) - 0.02 * myd1

        # Opportunistic: if moving to any resource cell directly, big bonus.
        if (nx, ny) in resources:
            v += 50

        # Avoid oscillation: prefer moves that don't increase distance to target too much.
        myd0 = cheb(sx, sy, tx, ty)
        v -= 0.15 * max(0, myd1 - myd0)

        if v > best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]