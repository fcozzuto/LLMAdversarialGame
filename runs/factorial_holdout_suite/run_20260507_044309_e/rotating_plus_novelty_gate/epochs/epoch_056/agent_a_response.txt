def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def md(a, b, c, d):
        ax = a - c; ax = ax if ax >= 0 else -ax
        by = b - d; by = by if by >= 0 else -by
        return ax + by

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            dcur = md(nx, ny, tx, ty)
            key = (dcur, valid.index((dx, dy, nx, ny)))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    res = [tuple(r) for r in resources]
    # Score: how much sooner we can reach a resource vs opponent
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in valid:
        # If we can immediately stand on a resource, prioritize it hard
        immediate = 0
        for (rx, ry) in res:
            if rx == nx and ry == ny:
                immediate = 1
                break

        best_for_move = None
        for (rx, ry) in res:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Prefer winning the race, then closeness
            lead = opd - myd  # positive means we arrive earlier
            # small tie-breakers: prefer shorter myd, and slightly prefer resources closer to center
            center = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
            key = (-lead, myd, center)
            if best_for_move is None or key < best_for_move:
                best_for_move = key
        key = (-(10 if immediate else 0), best_for_move)
        # deterministic: use first occurrence index as final tie-break
        full = (key, valid.index((dx, dy, nx, ny)))
        if best_key is None or full < best_key:
            best_key = full
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]