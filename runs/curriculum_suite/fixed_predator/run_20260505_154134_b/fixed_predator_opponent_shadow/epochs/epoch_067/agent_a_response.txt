def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    res = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.add((int(r[0]), int(r[1])))
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    occ = (sx, sy)
    if occ in res:
        return [0, 0]

    # choose next move that maximizes immediate advantage and resource progress
    best_move = [0, 0]
    best_val = -10**9
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # deterministic tie-break: fixed move order above
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        # advantage: prefer states where we are closer than opponent to resources
        self_to_opp = cheb(nx, ny, ox, oy)
        opp_to_self = cheb(ox, oy, nx, ny)  # same, kept for clarity
        # nearest resource from the candidate
        self_best = 10**9
        opp_best = 10**9
        for cx, cy in resources:
            d1 = cheb(nx, ny, cx, cy)
            if d1 < self_best:
                self_best = d1
            d2 = cheb(ox, oy, cx, cy)
            if d2 < opp_best:
                opp_best = d2

        # direct pick-up
        pick = 1 if (nx, ny) in res else 0

        # value combines (opp - self), resource distance (lower is better), and pickup
        # also slight bias away from opponent to avoid being outpaced behind them
        val = (opp_best - self_best) * 100 - self_best * 2 + pick * 10000 - self_to_opp * 1
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move