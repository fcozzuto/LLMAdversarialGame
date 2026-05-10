def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick target by maximizing opponent-relative access, with slight preference for nearer resources.
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # positive => we're closer
        # center bias breaks ties deterministically and avoids dithering
        center = - (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        key = (adv, -myd, center, -(rx + 13 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Aim to maximize advantage while still making progress toward the target.
        adv2 = opd2 - myd2
        center2 = - (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        # Also discourage unnecessary moves away from target
        progress = -(myd2)
        key = (adv2, progress, center2, -(nx + 17 * ny))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move