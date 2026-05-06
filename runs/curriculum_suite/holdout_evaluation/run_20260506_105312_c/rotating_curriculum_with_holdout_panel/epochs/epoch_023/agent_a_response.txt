def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Denial/interception: aim at what opponent is currently closest to.
    tx, ty = resources[0]
    best_opd = cheb(ox, oy, tx, ty)
    for rx, ry in resources[1:]:
        opd = cheb(ox, oy, rx, ry)
        if opd < best_opd:
            best_opd = opd
            tx, ty = rx, ry

    # If that target is missing for some reason, fall back to nearest to self.
    if (tx, ty) not in set(tuple(p) for p in resources):
        tx, ty = resources[0]
        best_my = cheb(sx, sy, tx, ty)
        for rx, ry in resources[1:]:
            myd = cheb(sx, sy, rx, ry)
            if myd < best_my:
                best_my = myd
                tx, ty = rx, ry

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        # Relative gain over opponent's proximity to the same target.
        rel = cheb(ox, oy, tx, ty) - myd
        # Small tie-break: prefer moves that also get us away from being trapped by obstacles.
        corner_bias = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            corner_bias = -0.05
        score = rel + corner_bias
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]