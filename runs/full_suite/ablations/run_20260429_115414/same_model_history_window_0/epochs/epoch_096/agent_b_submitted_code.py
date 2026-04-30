def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = set(obs)
    if not res:
        return [0, 0]

    def mdist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        my_best = 10**9
        opp_best = 10**9
        for r in res:
            d1 = mdist((nx, ny), r)
            if d1 < my_best: my_best = d1
            d2 = mdist((ox, oy), r)
            if d2 < opp_best: opp_best = d2
        val = my_best - 0.6 * opp_best + (0.01 * (abs(nx - ox) + abs(ny - oy)))
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]