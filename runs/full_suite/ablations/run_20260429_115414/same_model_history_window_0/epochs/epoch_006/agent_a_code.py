def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles if p is not None and len(p) == 2)

    def cheb(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        by = b - d
        if by < 0:
            by = -by
        return ax if ax > by else by

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_target = None
    best_val = -10**18
    if resources:
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = od - md
            if md == 0:
                val = 10**12
            if val > best_val or (val == best_val and (rx, ry) < (best_target[0], best_target[1]) if best_target else True):
                best_val = val
                best_target = (rx, ry)

    if best_target is None:
        best_target = (ox, oy)

    tx, ty = best_target
    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if w and (nx < 0 or nx >= w):
            continue
        if h and (ny < 0 or ny >= h):
            continue
        if (nx, ny) in obs:
            continue
        sc = cheb(nx, ny, tx, ty)
        if sc < best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]