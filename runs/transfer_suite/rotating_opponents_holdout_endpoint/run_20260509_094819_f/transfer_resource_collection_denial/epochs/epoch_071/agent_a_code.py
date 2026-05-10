def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    rpos = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                rpos.append((x, y))
    if not rpos:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_dist(x, y):
        bd = 10**9
        for rx, ry in rpos:
            d = cheb(x, y, rx, ry)
            if d < bd:
                bd = d
        return bd

    def min_advantage(x, y):
        # Positive means there exists a resource closer to us than to opponent (with Chebyshev distance).
        best = -10**9
        for rx, ry in rpos:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > best:
                best = adv
        return best

    candidates = [(-1, -1), (0, -1), (1, -1),
                  (-1, 0), (0, 0), (1, 0),
                  (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    # Early game: prioritize creating competitive advantage; late game: prioritize fastest collection.
    tr = int(observation.get("turns_remaining", 0) or 0)
    early = 1.0 if tr > 20 else 0.0
    late = 1.0 if tr <= 20 else 0.0

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            val = -10**12
        else:
            self_d = nearest_dist(nx, ny)
            opp_d = nearest_dist(ox, oy)
            adv = min_advantage(nx, ny)
            # Favor opponent being further from the same nearby resources.
            val = 10.0 * adv + (opp_d - self_d) + 0.02 * (opp_d - self_d)
            val = val * (0.7 + 0.3 * early) + (-0.9 * self_d) * late
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move