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

    if not resources:
        return [0, 0]

    # Pick a resource we can secure: prefer (opp closer -> bad), so maximize (opp_dist - self_dist)
    best = None
    best_key = None
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        # If we are closer (diff>=0) this key increases; also prefer nearer targets and those not too close to opponent
        key = (opp_d - self_d, -self_d, -(abs(cx - ox) + abs(cy - oy)), -cx, -cy)
        if best_key is None or key > best_key:
            best_key = key
            best = (cx, cy)

    tx, ty = best

    # Evaluate candidate moves with obstacle avoidance; choose move that improves our chance to reach target while not letting opponent get much closer.
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

            # Measure "security": how much closer we are than opponent, and how fast we converge to target.
            # Slightly penalize moving away from target.
            security = (opp_to_t - self_to_t)
            converge = -self_to_t

            # Also discourage moves that reduce our distance to opponent too much (keeps us from being intercepted).
            to_opp = cheb(nx, ny, ox, oy)
            avoid_intercept = to_opp

            val = (security, converge, avoid_intercept, -abs(nx - tx) - abs(ny - ty), -abs(nx - ox) - abs(ny - oy))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    # If all candidates blocked (rare), allow staying but still deterministic
    return best_move if best_move is not None else [0, 0]