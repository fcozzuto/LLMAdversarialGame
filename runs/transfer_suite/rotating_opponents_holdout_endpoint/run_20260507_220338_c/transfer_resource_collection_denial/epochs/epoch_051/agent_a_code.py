def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    # Target selection: maximize arrival advantage over opponent; tie-break by closeness.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        quad_bias = -((rx - ox) * (sx - ox) + (ry - oy) * (sy - oy))  # prefer resources "away" from opponent line
        key = (od - sd, -quad_bias, -sd)  # higher advantage, then strategic bias, then nearer
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Deterministic move choice with obstacle fallback: diag, x, y, stay.
    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for mvx, mvy in candidates:
        nx, ny = sx + mvx, sy + mvy
        if legal(nx, ny):
            return [mvx, mvy]
    return [0, 0]