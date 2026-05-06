def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # pick a target resource that maximizes our distance advantage
    best_cell = None
    best_adv = -10**18
    best_self_d = 10**18
    for cx, cy in resources:
        if not inb(cx, cy) or (cx, cy) in obs:
            continue
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        adv = opp_d - self_d
        # slight preference for closer collection once advantage ties
        key_self = self_d
        if adv > best_adv or (adv == best_adv and key_self < best_self_d):
            best_adv = adv
            best_self_d = key_self
            best_cell = (cx, cy)

    tx, ty = best_cell if best_cell is not None else (sx, sy)

    # choose a one-step move that improves our advantage toward the target
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # primary: increase advantage (opp_d - self_d)
        val = (opp_d - self_d) * 1000
        # secondary: if tied, move closer to target; and keep away from opponent
        val += (-self_d) * 10
        val += cheb(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]