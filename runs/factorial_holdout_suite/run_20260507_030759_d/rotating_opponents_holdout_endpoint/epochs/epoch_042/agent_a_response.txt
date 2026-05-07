def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def tdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy  # Chebyshev for king moves

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    best = None
    for tx, ty in res:
        my_t = tdist(sx, sy, tx, ty)
        op_t = tdist(ox, oy, tx, ty)
        # Prefer resources I can reach no later than opponent; then smallest gap; then nearer.
        key = (my_t > op_t, my_t - op_t, my_t, -op_t, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))

    _, (tx, ty) = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        dist_to = tdist(nx, ny, tx, ty)
        # Additional tie-break: prefer moves that also reduce opponent's ability (increase their dist).
        opp_dist = tdist(nx, ny, ox, oy)
        keym = (dist_to, -opp_dist, abs(tx - nx) + abs(ty - ny), dx, dy)
        if bestm is None or keym < bestm[0]:
            bestm = (keym, (dx, dy))
    if bestm is None:
        return [0, 0]
    dx, dy = bestm[1]
    return [dx, dy]