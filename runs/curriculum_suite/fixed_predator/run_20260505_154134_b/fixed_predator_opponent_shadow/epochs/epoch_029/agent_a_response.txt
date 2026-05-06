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
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose best target deterministically: maximize (opp_dist - self_dist), then minimize self_dist
    target = None
    best_key = None
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        key = (opp_d - self_d, -self_d, -abs(cx - sx), -abs(cy - sy), cx, cy)
        if best_key is None or key > best_key:
            best_key = key
            target = (cx, cy)
    if target is None:
        return [0, 0]
    tx, ty = target

    # Intercept/block: if opponent is close to some resource where we're not, bias toward that resource's direction
    opp_target = None
    opp_best = None
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        if opp_d < self_d:  # opponent has tempo
            key = (self_d - opp_d, -self_d, cx, cy)
            if opp_best is None or key > opp_best:
                opp_best = key
                opp_target = (cx, cy)

    aim = (tx, ty)
    if opp_target is not None:
        # Prefer aiming where opponent is threatening most, but still keep our chosen advantage target as fallback
        if opp_best[0] >= 1:
            aim = opp_target

    ax, ay = aim
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # primary: improve distance advantage toward aim resource
        cur_self = cheb(sx, sy, ax, ay)
        cur_opp = cheb(ox, oy, ax, ay)
        nxt_self = cheb(nx, ny, ax, ay)
        nxt_adv = (cur_opp - nxt_self)

        # secondary: keep moving toward our original target (even if aiming at block)
        nxt_self_t = cheb(nx, ny, tx, ty)
        cur_self_t = cheb(sx, sy, tx, ty)

        # tertiary: discourage standing still unless unavoidable
        still_pen = 1 if (dx == 0 and dy == 0) else 0

        # small tie-break using coordinates to keep determinism
        key2 = (nxt_adv, -(nxt_self_t), -(cur_self_t - nxt_self_t), -still_pen, nx, ny)
        if best_score is None or key2 > best_score:
            best_score = key2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]