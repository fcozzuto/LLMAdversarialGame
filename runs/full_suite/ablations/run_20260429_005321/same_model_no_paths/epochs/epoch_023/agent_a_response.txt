def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # Collect if already on resource
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    cx = (w - 1) // 2; cy = (h - 1) // 2

    # Pick target resource: maximize (opponent advantage - our disadvantage), with center tie-break
    if resources:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            rel = opd - myd  # positive means we are closer
            center_bias = - (cheb(rx, ry, cx, cy))  # prefer more central
            # If we are not close at all, still allow contesting later by keeping rel strong
            score = rel * 1000 + center_bias
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        # No visible resources: drift toward center while maximizing opponent distance
        tx, ty = cx, cy

    best_move = (None, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd1 = cheb(nx, ny, tx, ty)
        opd1 = cheb(ox, oy, tx, ty)

        # Prefer moves that reduce our distance to target and increase opponent's distance to same target
        # Also slightly discourage moving away from center to keep options open.
        center_pen = cheb(nx, ny, cx, cy)
        score = (opd1 - myd1) * 200 - myd1 * 10 - center_pen

        if best_move[0] is None or score > best_move[0]:
            best_move = (score, dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [best_move[1], best_move[2]]