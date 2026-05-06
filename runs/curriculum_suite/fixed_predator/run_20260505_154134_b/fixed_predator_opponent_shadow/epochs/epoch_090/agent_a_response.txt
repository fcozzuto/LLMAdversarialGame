def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = [(int(x), int(y)) for x, y in resources]
    for x, y in res:
        if (x, y) in obs:
            pass

    opp_best = None
    opp_best_d = None
    for cx, cy in res:
        d = cheb(ox, oy, cx, cy)
        if opp_best is None or d < opp_best_d:
            opp_best = (cx, cy)
            opp_best_d = d
    if opp_best is None:
        opp_best = res[0]

    def feasible(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    best_move = [0, 0]
    best_val = None
    alpha = 2

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not feasible(nx, ny):
                continue
            # evaluate assuming we compete for opponent's closest target
            tx, ty = opp_best
            self_d_now = cheb(sx, sy, tx, ty)
            self_d_new = cheb(nx, ny, tx, ty)
            opp_d_now = opp_best_d
            opp_d_new = cheb(ox, oy, tx, ty)  # opponent doesn't move in 1-step lookahead

            # also consider how much we deny opponent overall: distance to its closest target
            deny = (opp_d_new - opp_d_now)  # typically 0, but keep formula stable if target changes later
            # choose target that maximizes relative advantage among resources after our move
            best_rel = None
            for cx, cy in res:
                sd = cheb(nx, ny, cx, cy)
                od = cheb(ox, oy, cx, cy)
                rel = (od - sd, -sd)
                if best_rel is None or rel > best_rel:
                    best_rel = rel
            val = (best_rel[0] - alpha * deny, -self_d_new, -cheb(nx, ny, sx, sy))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move