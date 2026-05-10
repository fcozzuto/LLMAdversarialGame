def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (0, 0)
        bd = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, ox, oy)
            if bd is None or d < bd:
                bd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick target resource where we can beat the opponent (or the least lose).
    best_t = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        key = (opd - myd, -myd)  # maximize advantage, then minimize our distance
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t if best_t is not None else (sx, sy)

    # Choose move maximizing immediate advantage if we steer toward target.
    best_m = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)

        # If we step onto a resource, prioritize capturing.
        capture_bonus = 0
        if (nx, ny) in obstacles:
            capture_bonus = -10**9
        if (nx, ny) in resources:
            capture_bonus = 10**6

        # Favor moves that reduce distance more than the opponent can improve.
        # (Opponent doesn't move here, but this acts like a "reach earlier" heuristic.)
        dist_gain = (man(sx, sy, tx, ty) - myd)
        score = capture_bonus + (opd - myd) * 4 + dist_gain * 2 - (1 if dx == 0 and dy == 0 else 0)

        if best_score is None or score > best_score:
            best_score = score
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]