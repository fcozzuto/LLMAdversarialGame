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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        best = None
        best_key = None
        for cx, cy in resources:
            self_d = cheb(sx, sy, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # prioritize cells opp can reach sooner; then prioritize being closer; then left/up for determinism
            key = (opp_d - self_d, -self_d, -cx, -cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    if not resources:
        return [0, 0]

    tx, ty = pick_target()

    # score candidate moves: avoid obstacles, approach target, and avoid allowing opponent advantage
    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            self_to_t = cheb(nx, ny, tx, ty)
            opp_to_t = cheb(ox, oy, tx, ty)
            # opponent may move too, so favor increasing opponent's distance to target
            opp_dist_now = cheb(ox, oy, tx, ty)
            opp_dist_if = opp_dist_now  # unknown; proxy via our move: discourage moving into opponent's neighborhood
            opp_near = cheb(nx, ny, ox, oy)
            # also discourage getting too close to opponent unless it helps reaching target
            val = (-self_to_t, opp_to_t, opp_near, -cheb(nx, ny, tx, ty) + (opp_near >= 3))
            # deterministic tie-break by direction preference order implicitly via loop
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move