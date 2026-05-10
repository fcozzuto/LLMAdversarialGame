def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y, tx, ty):
        ax = abs(x - tx)
        ay = abs(y - ty)
        return ax if ax > ay else ay

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    near_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    i_am_evader = ("evader" in self_role) and ("pursuer" not in self_role)

    best_move = (0, 0)
    if i_am_evader:
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            tie = -(abs(nx - far_corner[0]) + abs(ny - far_corner[1]))
            v = d * 100000 + tie
            if v > bestv:
                bestv = v
                best_move = (dx, dy)
    else:
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            tie = abs(nx - near_corner[0]) + abs(ny - near_corner[1])
            v = (-d) * 100000 - tie
            if v > bestv:
                bestv = v
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]