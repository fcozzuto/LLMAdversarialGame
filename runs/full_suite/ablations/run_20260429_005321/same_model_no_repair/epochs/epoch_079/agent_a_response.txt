def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Drift to the corner farthest from opponent (tie-break by distance from own corner)
        far_corner = (0, 0)
        bestc = None
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        for cx, cy in corners:
            sc = cheb(cx, cy, ox, oy)
            t = cheb(cx, cy, sx, sy)
            key = (-sc, t, cx, cy)
            if bestc is None or key < bestc[0]:
                bestc = (key, dx, dy) if False else (key, None)
                far_corner = (cx, cy)
        tx, ty = far_corner
        best = None
        for dx, dy, nx, ny in legal:
            key = (cheb(nx, ny, tx, ty), -cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Race heuristic: maximize (opponent distance - my distance) to the most favorable resource.
    best = None
    for dx, dy, nx, ny in legal:
        my_best = None
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer capturing sooner and also resources the opponent can't reach quickly.
            # Also bias toward corner/center depending on opponent side deterministically via small term.
            bias = (rx + ry) - (w - 1 - rx + h - 1 - ry)
            val = (d_op - d_me) * 10 - d_me + (0.1 if bias >= 0 else -0.1)
            if my_best is None or val > my_best:
                my_best = val
        # Secondary: prefer positions that are close to some resource to avoid dead-end wandering.
        min_d = None
        for rx, ry in resources:
            dd = cheb(nx, ny, rx, ry)
            if min_d is None or dd < min_d:
                min_d = dd
        key = (-my_best, min_d, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]