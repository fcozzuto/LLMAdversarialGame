def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        by = b - d
        if by < 0:
            by = -by
        return ax + by

    if not resources:
        return [0, 0]

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and in_bounds(x, y):
                rs.append((x, y))
    if not rs:
        return [0, 0]

    # Choose target resource where we have best chance to arrive first.
    best_t = rs[0]
    best_key = None
    for x, y in rs:
        myd = man(sx, sy, x, y)
        opd = man(ox, oy, x, y)
        # Prefer resources we can reach sooner; break ties by bigger advantage and location.
        key = (myd, -(opd - myd), -(y), -(x))
        if best_key is None or key < best_key:
            best_key = key
            best_t = (x, y)

    tx, ty = best_t
    myd0 = man(sx, sy, tx, ty)
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Avoid moves that stall when progress is possible; maximize (opportunity - delay).
        progress_pen = 0
        if myd == myd0:
            progress_pen = 1
        key = (myd + progress_pen, -(opd - myd), -ny, -nx)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]