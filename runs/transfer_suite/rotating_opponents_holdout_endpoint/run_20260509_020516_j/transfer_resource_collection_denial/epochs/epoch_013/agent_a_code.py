def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for rx, ry in resources:
        if not inside(rx, ry):
            continue
        myd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if myd == 0:
            key = (10**9, 0, 0, -rx, -ry)
        else:
            center = -((rx - cx0) * (rx - cx0) + (ry - cy0) * (ry - cy0))
            key = (od - myd, -myd, center, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best[1], best[2]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        myd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        # Primary: keep a lead vs opponent at the target
        # Secondary: get closer to the target
        # Tertiary: drift toward center to avoid corner stagnation
        center2 = -((nx - cx0) * (nx - cx0) + (ny - cy0) * (ny - cy0))
        keym = (od2 - myd2, -myd2, center2, -nx, -ny)
        if bestm is None or keym > bestm[0]:
            bestm = (keym, dx, dy)

    return [int(bestm[1]), int(bestm[2])]