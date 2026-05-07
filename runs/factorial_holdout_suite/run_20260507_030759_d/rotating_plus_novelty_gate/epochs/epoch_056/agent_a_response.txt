def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if (sx, sy) in set(tuple(r) for r in resources):
        return [0, 0]
    if not resources:
        # fall back: move to reduce manhattan to opponent (deterministic)
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dself = abs(nx - ox) + abs(ny - oy)
            cand = (dself, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res_tuples = [tuple(r) for r in resources]
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_adv = None
        best_self = None
        best_opp = None
        for rx, ry in res_tuples:
            self_d = manh(nx, ny, rx, ry)
            opp_d = manh(nx, ny, rx, ry)
            adv = opp_d - self_d  # positive means we are closer than opponent
            if best_adv is None or (adv, -self_d, -opp_d, rx, ry) > (best_adv, -best_self, -best_opp, best_rx, best_ry):
                best_adv, best_self, best_opp, best_rx, best_ry = adv, self_d, opp_d, rx, ry
        # Prefer immediate pickup (self_d=0) implicitly via self_d; then maximize advantage; then minimize own dist
        cand = (-best_adv, best_self, best_opp, dx, dy)
        if best is None or cand < best:
            best = cand
    return [best[3], best[4]]