def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        if myd <= oppd:
            sc = 2000000 + (oppd - myd) * 2000 - myd
        else:
            sc = 1000 + (oppd - myd) * 20
        if best is None or sc > best[0]:
            best = (sc, rx, ry)

    _, tx, ty = best
    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # Try the greedy direction; if blocked or off-grid, consider alternatives by score.
    gx, gy = sx + dx, sy + dy
    if inside(gx, gy) and (gx, gy) not in obstacles:
        return [dx, dy]

    best_move = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        if myd <= oppd:
            sc = 500000 - myd * 5 + (oppd - myd) * 200
        else:
            sc = 10000 - myd * 2 + (oppd - myd) * 10
        if best_move is None or sc > best_move[0]:
            best_move = (sc, mdx, mdy)
    if best_move is None:
        return [0, 0]
    return [best_move[1], best_move[2]]