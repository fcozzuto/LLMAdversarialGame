def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_dist(x, y, prefer=None):
        b = 10**18
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < b: b = d
        return b

    opp_best = best_dist(ox, oy)
    best = (10**18, -10**18, 10**18, 0, 0)  # self_d, gain, opp_d, dx, dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        if (nx, ny) in obstacles and (sx, sy) not in obstacles:
            continue

        self_best = best_dist(nx, ny)
        opp_d = opp_best
        gain = opp_d - self_best  # larger is better
        # tie-break deterministically by closer self, then larger gain, then smaller dx+dy magnitude, then order
        key = (self_best, gain, -opp_d, abs(dx) + abs(dy), dx, dy)
        if key < (best[0], best[1], best[2], best[3], best[4], best[5]):
            best = (self_best, gain, opp_d, abs(dx) + abs(dy), dx, dy)

    return [int(best[4]), int(best[5])]