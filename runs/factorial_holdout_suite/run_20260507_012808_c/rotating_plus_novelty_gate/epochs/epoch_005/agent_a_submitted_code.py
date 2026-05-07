def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set(obstacles) if obstacles else set()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_val = None
    best_move = [0, 0]

    if resources:
        def nearest_dist(x, y):
            d = None
            for rx, ry in resources:
                t = cheb(x, y, rx, ry)
                if d is None or t < d:
                    d = t
            return d
        my_opp = nearest_dist(ox, oy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            my_d = nearest_dist(nx, ny)
            if my_d is None:
                continue
            val = (my_opp - my_d) - 0.01 * cheb(nx, ny, ox, oy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        tx, ty = ox, oy
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            val = -cheb(nx, ny, tx, ty)
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move