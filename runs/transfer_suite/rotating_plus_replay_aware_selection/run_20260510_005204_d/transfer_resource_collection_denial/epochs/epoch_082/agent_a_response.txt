def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick the resource that maximizes how much closer we can get than the opponent (chebyshev).
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Primary: maximize advantage; Secondary: prefer smaller myd to finish sooner.
        # Tertiary: deterministic tie-break by coordinates.
        key = (opd - myd, -myd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    tx, ty = best[1], best[2]

    # If we can collect immediately, stay.
    if sx == tx and sy == ty:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, -10**9, 0, 0)
    opd0 = cheb(ox, oy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd1 = cheb(nx, ny, tx, ty)
        # Main objective: maximize advantage at next step, then minimize our distance.
        # Small penalty for allowing opponent to get closer (avoid moving "into" their path).
        oppd1 = cheb(ox, oy, tx, ty)
        util = (opd0 - myd1) * 1000 - myd1 * 10 - (cheb(ox, oy, nx, ny) - 1)
        # Deterministic tie-break: prefer smaller dx, then smaller dy.
        tdx = -abs(dx)
        tdy = -abs(dy)
        cand = (util, tdx, tdy, -nx, -ny, dx, dy)
        if best_move[0] is None or cand > best_move:
            best_move = (util, tdx, tdy, dx, dy)

    dx, dy = best_move[3], best_move[4]
    return [dx, dy]