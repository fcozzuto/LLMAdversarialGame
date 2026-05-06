def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    res = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    resources = [(int(p[0]), int(p[1])) for p in res]
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_key = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        nearest_self = 10**9
        best_margin = -10**9
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            if self_d < nearest_self:
                nearest_self = self_d
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - self_d
            if margin > best_margin:
                best_margin = margin

        dist_opp = cheb(nx, ny, ox, oy)

        if best_margin > 0:
            key = (1, best_margin, -nearest_self, dist_opp)
        else:
            key = (0, -nearest_self, dist_opp, 0)

        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_move else [0, 0]