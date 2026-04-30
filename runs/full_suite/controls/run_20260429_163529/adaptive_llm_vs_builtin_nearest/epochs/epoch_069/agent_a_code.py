def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        best = None
        bestd = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                    continue
                d = cheb(nx, ny, tx, ty)
                key = (d, -abs(ox - nx) - abs(oy - ny), nx, ny)
                if best is None or key < bestd:
                    best = [dx, dy]
                    bestd = key
        if best is None:
            return [0, 0]
        return best

    opp_best_d = None
    opp_best = None
    self_best_d = None
    self_best = None
    for (x, y) in res:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        if self_best is None or (ds, x, y) < (self_best_d, self_best[0], self_best[1]):
            self_best_d = ds
            self_best = (x, y)
        if opp_best is None or (do, x, y) < (opp_best_d, opp_best[0], opp_best[1]):
            opp_best_d = do
            opp_best = (x, y)

    sx_d = cheb(sx, sy, self_best[0], self_best[1])
    ox_d = cheb(ox, oy, self_best[0], self_best[1])
    if sx_d <= ox_d:
        return step_toward(self_best[0], self_best[1])
    return step_toward(opp_best[0], opp_best[1])