def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any((sx, sy) == tuple(r) for r in resources):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        tx, ty = cx, cy
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # Pick resource with best "race" score; if tied, prefer closer to us.
    best_r = None
    best_rv = (-10**18, 10**18)
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # advantage positive => we are closer
        rv = (opd - myd, myd)
        if rv > best_rv:
            best_rv = rv
            best_r = (rx, ry)

    rx, ry = best_r
    # Intercept bias: if opponent is closer, target the neighbor cell that moves us closer to being on their route.
    if cheb(ox, oy, rx, ry) < cheb(sx, sy, rx, ry):
        ix, iy = rx, ry
        # Move "away from" opponent direction (deterministic)
        step_x = 0 if ox == rx else (1 if rx > ox else -1)
        step_y = 0 if oy == ry else (1 if ry > oy else -1)
        ix = rx - step_x
        iy = ry - step_y
        if not valid(ix, iy):
            ix, iy = rx, ry
        target_x, target_y = ix, iy
    else:
        target_x, target_y = rx, ry

    best_m = (0, 0)
    best_val = (-10**18, 10**18, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_to = cheb(nx, ny, target_x, target_y)
        my_to_r = cheb(nx, ny, rx, ry)
        op_to_r = cheb(ox, oy, rx, ry)
        # Maximize: reduce distance to target, then reduce distance to resource, and (weakly) favor states where opponent is farther from resource.
        val = (-my_to, -my_to_r, op_to_r)
        # tie-break: deterministic by move order already
        if val > best_val:
            best_val = val
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]