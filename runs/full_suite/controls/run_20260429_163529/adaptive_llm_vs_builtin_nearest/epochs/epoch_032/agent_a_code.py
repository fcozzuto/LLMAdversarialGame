def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        a = dx if dx >= 0 else -dx
        b = dy if dy >= 0 else -dy
        return a if a > b else b

    # Choose resource where we are most ahead in "arrival" distance; tie-break by being closer.
    best_t = None
    best_key = None
    for tx, ty in res:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        key = (ds - do, ds, tx + ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)
    tx, ty = best_t

    # Evaluate candidate single-step moves; avoid obstacles.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nds = cheb(nx, ny, tx, ty)
        # Also penalize letting opponent be closer (using current opponent distance as proxy).
        do = cheb(ox, oy, tx, ty)
        key = (nds - do, nds, (nx + ny), dx * dx + dy * dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]