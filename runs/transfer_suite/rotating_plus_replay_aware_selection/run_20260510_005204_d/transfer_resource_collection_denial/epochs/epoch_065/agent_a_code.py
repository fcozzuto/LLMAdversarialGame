def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    res_list = observation.get("resources", None) or []
    obs_list = observation.get("obstacles", None) or []

    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick resource that we can reach sooner than opponent; tie-break deterministically by closer then coord.
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - myd, -myd, rx, ry)  # maximize (opd-myd), then closer
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    # If adjacent (or same), step onto it if possible.
    best_step = [0, 0]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if (tx, ty) in resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) == (tx, ty):
                return [dx, dy]

    # Move greedily toward target (Chebyshev).
    # Try steps in deterministic order to break ties.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                d = cheb(nx, ny, tx, ty)
                candidates.append((d, dx, dy))
    if candidates:
        candidates.sort(key=lambda t: (t[0], t[2], t[1]))  # deterministic tie-break
        return [candidates[0][1], candidates[0][2]]

    # If blocked, stay if valid else pick any valid move.
    if inb(sx, sy):
        return [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
    return [0, 0]