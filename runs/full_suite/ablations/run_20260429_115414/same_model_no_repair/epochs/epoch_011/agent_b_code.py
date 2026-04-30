def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    tx, ty = None, None
    if resources:
        scored = []
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer targets where we're not behind, otherwise close the gap.
            lead = opd - myd
            not_behind = 1 if lead >= 0 else 0
            # Bias toward upper-left half deterministically to change behavior.
            center_bias = -((rx + ry) / (w + h))
            key = (not_behind, lead, center_bias, -rx, -ry, -myd)
            scored.append((key, (rx, ry)))
        scored.sort(reverse=True)
        tx, ty = scored[0][1]
    else:
        tx, ty = w - 1, h - 1

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = (None, None, None)
    curd = cheb(sx, sy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # If tied, avoid giving opponent a similar improvement: choose move that worsens opponent-to-target the most.
        opd_cur = cheb(ox, oy, tx, ty)
        opd_nxt = cheb(ox, oy, tx, ty)  # opponent doesn't move now; keep deterministic tie-break
        prog = curd - nd
        key = (prog, -abs(nx - ox) - abs(ny - oy), -nd, dx, dy)
        if best[0] is None or key > best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]