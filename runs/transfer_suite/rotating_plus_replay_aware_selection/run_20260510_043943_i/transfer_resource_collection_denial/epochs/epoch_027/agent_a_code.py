def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    if resources:
        best_r = None
        best_cmp = None
        best_dist = None
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            cmp = opd - myd
            if best_r is None or cmp > best_cmp or (cmp == best_cmp and myd < best_dist):
                best_r = (rx, ry)
                best_cmp = cmp
                best_dist = myd
        tx, ty = best_r
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = (0, 0)
    best_score = -10**30
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(nx, ny, ox, oy)
        # Prefer getting closer to target, while staying away from opponent when not at target.
        score = -myd + 0.05 * opd
        # Small deterministic tie-break to reduce oscillation near target:
        score -= 0.001 * (abs(dx) + abs(dy))
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]