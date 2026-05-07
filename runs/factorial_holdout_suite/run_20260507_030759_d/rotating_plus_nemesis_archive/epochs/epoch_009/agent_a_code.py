def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Deterministic order for equal keys
    resources_sorted = sorted((int(x), int(y)) for x, y in resources)

    best_t = resources_sorted[0]
    best_key = None
    for tx, ty in resources_sorted:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        key = (opd - myd, -myd, -((tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_mv = (0, 0)
    best_mv_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer moves that keep ahead (higher opd-myd), then closer, then avoid getting "stuck"
        stuck_pen = (dx == 0 and dy == 0)
        key = (opd - myd, -myd, -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)), -stuck_pen, dx, dy)
        if best_mv_key is None or key > best_mv_key:
            best_mv_key = key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]