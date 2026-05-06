def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        bestm = (0, 0)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best:
                best, bestm = d, (dx, dy)
        return [bestm[0], bestm[1]]

    # Choose a resource to compete for: prefer cells where we can become closer than opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        key = (oppd - myd, -myd)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        tx, ty = w // 2, h // 2
        best = None
        bestm = (0, 0)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best:
                best, bestm = d, (dx, dy)
        return [bestm[0], bestm[1]]

    tx, ty = best_res

    # Evaluate next moves by how much we improve our lead over opponent for the same target,
    # with a small tie-breaker toward overall closeness.
    best_score = None
    bestm = (0, 0)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        oppd2 = cheb(ox, oy, tx, ty)
        lead = oppd2 - myd2  # higher is better (we get closer / deny)
        score = (lead, -myd2)
        if best_score is None or score > best_score:
            best_score = score
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]