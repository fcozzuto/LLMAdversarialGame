def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obs_raw = observation.get("obstacles") or []
    obstacles = obs_raw if isinstance(obs_raw, set) else set(tuple(p) for p in obs_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        self_best = None
        self_best_ds = None
        opp_best = None
        best_adv = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            key = (adv, -ds, -do, rx, ry)
            if self_best is None or key > self_best:
                self_best = key
                self_best_ds = ds
                opp_best = do
                best_adv = adv

        if self_best is None:
            continue

        key2 = (self_best[0], self_best[1], self_best[2], -abs(nx - ox) - abs(ny - oy), -cheb(ox, oy, nx, ny))
        if best_key is None or key2 > best_key:
            best_key = key2
            best_move = [dx, dy]

    return best_move