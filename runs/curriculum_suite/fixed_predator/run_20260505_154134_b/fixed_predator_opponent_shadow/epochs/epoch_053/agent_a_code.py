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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        if not resources:
            return None
        best = None
        best_key = None
        for cx, cy in resources:
            sd = cheb(sx, sy, cx, cy)
            od = cheb(ox, oy, cx, cy)
            # Prefer cells where we are relatively closer than opponent (or least worse),
            # and break ties deterministically toward lower coordinates.
            key = (-(od - sd), sd, -cx, -cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    tx_ty = pick_target()
    if tx_ty is None:
        return [0, 0]
    tx, ty = tx_ty

    best_move = [0, 0]
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue

            sd_next = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Main: maximize advantage (opponent closer - us closer), i.e., we want od - sd_next large.
            adv = od - sd_next

            # Secondary: avoid giving opponent immediate access to a nearby resource cluster.
            # Approximate by preferring moves that increase our chebyshev distance to opponent
            # when we are not already clearly winning the target.
            opp_close_pen = 0
            if adv <= 0:
                opp_close_pen = 0.15 * cheb(nx, ny, ox, oy)

            # Tertiary deterministic: prefer smaller distance to target to reduce oscillation.
            sc = adv - opp_close_pen - 0.01 * sd_next

            if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = sc
                best_move = [dx, dy]

    return best_move