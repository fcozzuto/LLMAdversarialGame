def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def step_target(tx, ty, favor="beat"):
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        if favor == "beat" and myd > opd:
            return 10**9, myd - opd, myd
        return 0, opd - myd, myd

    best = None
    best_key = (10**18, 10**18, 10**18)
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        beat = myd - opd  # smaller means more advantage
        key = (-(opd - myd), beat, myd)  # maximize (opd-myd), minimize beat, then myd
        if key < best_key:
            best_key = key
            best = (rx, ry)

    if not best:
        return [0, 0]
    tx, ty = best

    best_move = [0, 0]
    best_score = (10**18, 10**18, 10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        score = (myd - opd, myd, (abs(nx - ox) + abs(ny - oy)))
        if score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move