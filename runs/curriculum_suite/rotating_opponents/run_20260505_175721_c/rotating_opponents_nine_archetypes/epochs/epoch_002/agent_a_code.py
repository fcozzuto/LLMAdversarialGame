def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            adv = opd - myd  # positive means I'm closer
            key = (-adv, myd, ry, rx)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    best = (0, 0)
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            myd = dist(nx, ny, tx, ty)
            opd = dist(nx, ny, ox, oy)
            # If stepping onto opponent, strongly prefer it
            coll = 1 if (nx, ny) == (ox, oy) else 0
            # minimize: my distance, then prefer larger opponent distance, then collisions as bonus
            score = (myd - 3 * coll, -opd, dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]