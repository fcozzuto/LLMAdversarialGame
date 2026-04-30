def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dy >= 0 else -dy

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        best = None
        # Score resources by advantage over opponent (closer to us than opponent)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds
            # Tie-break deterministically by coordinates
            key = (-(adv), ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w // 2, h // 2)

    # Candidate moves: deterministic ordering
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            cand.append((dx, dy, nx, ny))

    best_move = None
    best_key = None
    for dx, dy, nx, ny in cand:
        # Prefer reducing distance to target; slight preference to not overshoot
        dcur = dist(sx, sy, tx, ty)
        dnew = dist(nx, ny, tx, ty)
        delta = dcur - dnew
        # Tie-break: prefer moves that also approach opponent's likely area (soft pressure)
        dop = dist(ox, oy, tx, ty)
        key = (-delta, abs(dnew - dop) , dx, dy, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]