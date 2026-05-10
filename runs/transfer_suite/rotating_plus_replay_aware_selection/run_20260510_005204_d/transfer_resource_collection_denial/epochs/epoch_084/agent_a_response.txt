def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick best resource by reaching advantage (opponent distance - my distance).
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; if not, still contest by minimizing worst-case.
        # Deterministic tie-breakers: smaller myd, then lexicographic coords.
        key = (opd - myd, -myd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    tx, ty = best[1], best[2]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_d = curd
    # Greedy step toward target with obstacle awareness.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Primary: reduce distance; tie-break deterministic by direction order (already fixed).
        if nd < best_d:
            best_d = nd
            best_move = [dx, dy]
        elif nd == best_d:
            # Prefer moves that also improve opponent denial slightly: increase distance-to-target for opponent.
            od = cheb(ox, oy, tx, ty)
            if cheb(ox, oy, tx, ty) > od:
                best_move = [dx, dy]

    return best_move