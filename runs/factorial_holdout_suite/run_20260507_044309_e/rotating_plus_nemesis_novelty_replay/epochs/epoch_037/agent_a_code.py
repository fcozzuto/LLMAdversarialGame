def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def clamp_x(x): 
        return 0 if x < 0 else (w - 1 if x >= w else x)

    def clamp_y(y):
        return 0 if y < 0 else (h - 1 if y >= h else y)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def on_resource(x, y):
        for rx, ry in res:
            if rx == x and ry == y:
                return True
        return False

    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = clamp_x(sx + dx), clamp_y(sy + dy)
        if (nx, ny) in obstacles:
            continue
        # Evaluate best attainable advantage from this next position.
        max_adv = -10**9
        best_ds = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we can be earlier
            if adv > max_adv or (adv == max_adv and (best_ds is None or ds < best_ds or (ds == best_ds and (rx, ry) < (minx, miny) if False else True))):
                max_adv = adv
                best_ds = ds
        # Boost if landing on a resource.
        val = max_adv + (3 if on_resource(nx, ny) else 0)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]