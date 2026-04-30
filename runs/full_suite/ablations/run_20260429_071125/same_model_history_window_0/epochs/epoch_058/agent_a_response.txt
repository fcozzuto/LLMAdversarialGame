def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obstacle_set = {(p[0], p[1]) for p in obstacles}
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacle_set:
            continue
        # resource targeting: maximize how much closer we are relative to opponent
        rel_best = -10**9
        reach_bonus = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            rel = opd - myd  # higher is better (we are catching up)
            if myd == 0:
                reach_bonus = 5000
                rel = 10**9
            if rel > rel_best:
                rel_best = rel
        if not resources:
            rel_best = -cheb(nx, ny, ox, oy)
        # discourage running into opponent unless we're actually contesting
        opp_dist = cheb(nx, ny, ox, oy)
        contest_scale = 1.0 if rel_best > 0 else 0.4
        score = reach_bonus + 100 * rel_best + contest_scale * (opp_dist) - 1.5 * (1 if (nx, ny) in obstacle_set else 0)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        # If all moves blocked, stay
        return [0, 0]
    return [int(best[0]), int(best[1])]