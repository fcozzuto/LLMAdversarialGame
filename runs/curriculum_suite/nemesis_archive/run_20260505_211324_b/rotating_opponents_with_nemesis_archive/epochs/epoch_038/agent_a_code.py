def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Opponent greedy target (nearest_resource behavior assumption)
    opp_target = min(res, key=lambda p: (md(ox, oy, p[0], p[1]), p[0], p[1]))

    # Choose a resource that opponent is unlikely to take next.
    # Score favors (opp_dist - self_dist) but penalizes closeness to opponent greedy target.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def heuristic(p):
        myd = md(sx, sy, p[0], p[1])
        opd = md(ox, oy, p[0], p[1])
        base = (opd - myd) * 5 - myd
        # If it's the opponent's nearest resource, make it much less attractive.
        if p == opp_target:
            base -= 1000
        # If close in distance to opponent greedy's target, they may switch quickly.
        dist_to_opp_target = md(p[0], p[1], opp_target[0], opp_target[1])
        base -= (4 - min(4, dist_to_opp_target)) * 25
        # Mild bias toward central paths to reduce tie degeneracy.
        center_bias = - (abs(p[0] - cx) + abs(p[1] - cy)) * 0.01
        return base + center_bias

    target = min(res, key=lambda p: (-heuristic(p), md(sx, sy, p[0], p[1]), p[0], p[1]))

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]