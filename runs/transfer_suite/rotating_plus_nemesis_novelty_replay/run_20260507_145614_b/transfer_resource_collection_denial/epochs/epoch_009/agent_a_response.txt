def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp_to_valid(x, y):
        best = None
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                d = cheb(nx, ny, x, y)
                if best is None or d < best[0] or (d == best[0] and (nx, ny) < best[1]):
                    best = (d, (nx, ny))
        return best[1] if best else (x, y)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bestd, bestm = 10**9, (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) < bestm):
                bestd, bestm = d, (dx, dy)
        return [bestm[0], bestm[1]]

    best_key = None
    best_tx, best_ty = resources[0]
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer than opponent (margin), then smaller self distance.
        margin = od - sd
        key = (-(margin), sd, (rx, ry))
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = rx, ry

    bestd, bestm = 10**9, (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, best_tx, best_ty)
        # If landing on a resource cell, prioritize strongly and deterministically.
        if (nx, ny) in set(tuple(r) for r in resources):
            d = -1
        if d < bestd or (d == bestd and (dx, dy) < bestm):
            bestd, bestm = d, (dx, dy)

    if (sx + bestm[0], sy + bestm[1]) == (sx, sy):
        # Still allowed: nudge deterministically toward best target if possible.
        gx, gy = clamp_to_valid(best_tx, best_ty)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and cheb(nx, ny, gx, gy) < cheb(sx, sy, gx, gy):
                return [dx, dy]
    return [bestm[0], bestm[1]]