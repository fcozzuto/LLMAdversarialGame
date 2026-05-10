def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    role = str(observation.get("self_role") or "").lower()
    self_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)

    if (sx, sy) == (ox, oy):
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Prefer reducing/increasing Chebyshev distance; tie-break by local freedom and obstacle safety.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist((nx, ny), (ox, oy))
        if self_evader:
            primary = -d
        else:
            primary = d
        # Local freedom: count legal neighboring cells.
        free = 0
        for ex, ey in moves:
            tx, ty = nx + ex, ny + ey
            if ok(tx, ty):
                free += 1
        # Obstacle proximity: penalize being adjacent to blocked cells.
        adj = 0
        for ex, ey in moves:
            tx, ty = nx + ex, ny + ey
            if (tx, ty) in blocked:
                adj += 1
        # Deterministic tie-break: lexicographic on move.
        key = (primary, -free, adj, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]