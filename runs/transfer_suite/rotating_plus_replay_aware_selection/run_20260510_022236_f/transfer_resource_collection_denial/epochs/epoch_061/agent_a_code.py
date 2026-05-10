def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_obs_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                    pen += 1
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    # Deterministic tie-break: iterate in fixed order, keep first best.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        my_pen = adj_obs_pen(nx, ny)
        # Evaluate racing to the most favorable remaining resource.
        cur_best = -10**18
        for rx, ry in res:
            d_self = cheb_dist(nx, ny, rx, ry)
            d_opp = cheb_dist(ox, oy, rx, ry)
            # Prefer immediate pickup and resources the opponent is relatively farther from.
            val = (d_opp - d_self) * 3 + (-d_self) * 1.0 + (10 if d_self == 0 else 0)
            # Slightly discourage stepping into tight obstacle adjacency when targeting far points.
            val -= my_pen * (2 if d_self > 0 else 0)
            if val > cur_best:
                cur_best = val
        # If no resource evaluation happened (shouldn't), fallback to staying safe.
        if cur_best == -10**18:
            cur_best = -my_pen
        if cur_best > best_val:
            best_val = cur_best
            best_move = [dx, dy]

    return best_move