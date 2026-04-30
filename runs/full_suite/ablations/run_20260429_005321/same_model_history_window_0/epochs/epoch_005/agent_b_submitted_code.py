def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = set(obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_key = None

    if resources:
        do = None
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            if do is None or d < do:
                do = d

        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obs:
                continue
            ds = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if ds is None or d < ds:
                    ds = d
            adv = do - ds
            key = (adv, -ds, dx == 0 and dy == 0)
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            dist = cheb(nx, ny, ox, oy)
            key = (dist, dx == 0 and dy == 0)
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best