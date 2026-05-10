def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set(obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_r = None
    best_margin = None
    best_ds = None
    best_rx = None
    best_ry = None

    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # bigger is better (arrive earlier)
        if best_r is None or margin > best_margin or (margin == best_margin and (ds < best_ds or (ds == best_ds and (rx, ry) < (best_rx, best_ry)))):
            best_r = (rx, ry)
            best_margin = margin
            best_ds = ds
            best_rx, best_ry = rx, ry

    tx, ty = best_r

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dxdy = (0, 0)
    best_score1 = -10**9
    best_score2 = 10**9
    best_score3 = 10**9

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if w and (nx < 0 or nx >= w): 
            continue
        if h and (ny < 0 or ny >= h):
            continue
        if (nx, ny) in obstacle_set:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        margin2 = do2 - ds2
        if margin2 > best_score1 or (margin2 == best_score1 and (ds2 < best_score2 or (ds2 == best_score2 and (nx, ny) < (sx + best_dxdy[0], sy + best_dxdy[1])))):
            best_score1 = margin2
            best_score2 = ds2
            best_score3 = nx + ny
            best_dxdy = (dx, dy)

    dx, dy = best_dxdy
    return [dx, dy]