def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            key = (d, nx + ny)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Resource-denial heuristic: maximize how much closer we become than opponent for some resource.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        own_best = 10**9
        opp_best = -10**9
        for r in resources:
            rx, ry = r[0], r[1]
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            own_best = sd if sd < own_best else own_best
            gap = od - sd  # positive means we are closer than opponent
            if gap > opp_best:
                opp_best = gap
                best_r = (rx, ry, sd, od)
            # no else: keep opp_best
        # Prefer breaking ties by also minimizing our closest distance, then keeping away from obstacles implicitly via legality.
        # Add a small preference to reduce opponent's "being closer" for the contested target.
        rx, ry, sd, od = best_r
        key = (-opp_best, sd, od, nx - ox, ny - oy, nx + ny)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]