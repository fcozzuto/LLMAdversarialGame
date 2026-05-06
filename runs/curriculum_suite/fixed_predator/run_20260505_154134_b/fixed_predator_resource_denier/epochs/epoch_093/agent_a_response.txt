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

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            t = (d, nx + ny)
            if best is None or t < best[0]:
                best = (t, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    best_score = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        min_self = 10**9
        max_delta = -10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd < min_self:
                min_self = sd
            delta = od - sd  # positive means we are closer than opponent to this resource
            if delta > max_delta:
                max_delta = delta
        # prioritize securing a resource where we are ahead; otherwise minimize our distance
        score = max_delta * 100 - min_self
        tiebreak = (min_self, -(dx * 10 + dy))
        cur = (-(score), tiebreak)
        if best_score is None or cur < best_score:
            best_score = cur
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]