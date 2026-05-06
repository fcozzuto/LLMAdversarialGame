def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target we can realistically beat (avoid resources opponent is about to take)
    best_r = None
    best_key = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        if d_opp <= 1:
            key = (-10**9, 10**9)  # heavily avoid
        else:
            key = (d_opp - d_self, -d_self)  # maximize advantage, then prefer closer
        if best_key is None or key > best_key or (key == best_key and (rx, ry) < best_r):
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    rx, ry = best_r

    # Choose move that best approaches target, while also improving our advantage versus opponent
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self2 = cheb(nx, ny, rx, ry)
        d_opp2 = cheb(ox, oy, rx, ry)  # opponent position unchanged this turn
        score = (-(d_self2), (d_opp2 - d_self2), -abs(nx - rx) - abs(ny - ry))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]