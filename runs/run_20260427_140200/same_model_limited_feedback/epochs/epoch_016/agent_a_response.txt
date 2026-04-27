def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)
    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy
    res_list = [(x, y) for (x, y) in resources if (x, y) not in obstacles]
    if not res_list:
        # No visible resources: move to maximize distance from opponent along a safe step
        bestd = -10**9
        best = (0, 0)
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            score = cheb(nx, ny, ox, oy)
            if score > bestd:
                bestd = score
                best = (dx, dy)
        return [best[0], best[1]]
    # Select best target based on closeness, slight preference for being far from opponent
    best_target = None
    best_metric = 10**9
    for rx, ry in res_list:
        m = dist(sx, sy, rx, ry)
        # tie-breaker: prefer resources less reachable by opponent
        m2 = dist(ox, oy, rx, ry)
        metric = (m, -m2, rx, ry)
        if metric < (best_metric, 0, -1, -1):
            best_metric = metric[0]
            best_target = (rx, ry)
    tx, ty = best_target
    # Evaluate candidate moves deterministically
    best_score = -10**18
    best_move = (0, 0)
    opp_dist_now = dist(sx, sy, ox, oy)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = dist(nx, ny, tx, ty)
        d_to_t_cheb = cheb(nx, ny, tx, ty)
        d_opp = dist(nx, ny, ox, oy)
        # If moving onto an adjacent resource likely to be collected next, give a boost
        on_res = 1 if (nx, ny) in set(tuple(p) for p in res_list) else 0
        # Prefer reducing distance to target, while not letting opponent get much closer
        score = (-3 * d_to_t - 1.5 * d_to_t_cheb) + 4.0 * on_res + (0.6 * (d_opp - opp_dist_now))
        # If we'd move adjacent to opponent, slightly penalize to avoid collisions/blocks
        if cheb(nx, ny, ox, oy) <= 1:
            score -= 2.0
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]