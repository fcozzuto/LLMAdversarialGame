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

    if not resources:
        return [0, 0]

    # Pick the resource where we can reach at least as fast, otherwise the best advantage.
    best = None
    best_key = None
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        adv = opp_d - self_d
        key = (1 if adv >= 0 else 0, adv, -self_d, -cx, -cy)
        if best_key is None or key > best_key:
            best_key = key
            best = (cx, cy)

    tx, ty = best

    # Evaluate next moves with local obstacle avoidance and advantage improvement.
    best_move = [0, 0]
    best_move_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            self_d2 = cheb(nx, ny, tx, ty)
            opp_d2 = cheb(ox, oy, tx, ty)
            adv2 = opp_d2 - self_d2
            # Prefer capturing soon; also prefer improving advantage; keep distance to opponent if tied.
            key = (adv2, -self_d2, -cheb(nx, ny, ox, oy), -dx, -dy)
            if best_move_key is None or key > best_move_key:
                best_move_key = key
                best_move = [dx, dy]

    return best_move if best_move_key is not None else [0, 0]