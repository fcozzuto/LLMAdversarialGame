def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def min_dist_to_obstacles(x, y):
        m = 10**9
        for ox2, oy2 in obstacles:
            d = abs(x - ox2) + abs(y - oy2)
            if d < m:
                m = d
        return m if m != 10**9 else 10**6

    nearest_res = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                nearest_res = (rx, ry)

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)
        d_obs = min_dist_to_obstacles(nx, ny)

        if pursuer:
            # Primary: minimize distance to opponent (capture in Chebyshev=0).
            # Secondary: maximize clearance from obstacles.
            # Tertiary: reduce distance to nearest resource (if any) to avoid stalling near obstacles.
            res_term = 0
            if nearest_res is not None:
                res_term = cheb(nx, ny, nearest_res[0], nearest_res[1])
            score = (-d_op, -d_obs, res_term)
        else:
            # Evader: maximize distance from pursuer, keep distance from obstacles,
            # and (if possible) head toward the farthest corner.
            corner_targets = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corner_targets, key=lambda c: cheb(c[0], c[1], ox, oy))
            corner_bias = cheb(nx, ny, far_corner[0], far_corner[1])
            score = (d_op, -d_obs, corner_bias)

        if best is None:
            best = (dx, dy)
            best_score = score
        else:
            if pursuer:
                if score < best_score:
                    best = (dx, dy)
                    best_score = score
            else:
                if score > best_score:
                    best = (dx, dy)
                    best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]