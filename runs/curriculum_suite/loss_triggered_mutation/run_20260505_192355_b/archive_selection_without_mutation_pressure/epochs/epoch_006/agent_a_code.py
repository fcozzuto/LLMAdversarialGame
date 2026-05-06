def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    legal_moves = [(dx, dy) for dx, dy in moves if legal(sx + dx, sy + dy)]
    if not legal_moves:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def edge_bonus(x, y):
        d = min(x, w - 1 - x, y, h - 1 - y)
        return d if d < 2 else 0

    if not resources:
        best = legal_moves[0]
        bestv = -10**18
        for dx, dy in legal_moves:
            nx, ny = sx + dx, sy + dy
            v = man(nx, ny, ox, oy) + 2 * edge_bonus(nx, ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best = legal_moves[0]
    bestv = -10**18
    for dx, dy in legal_moves:
        nx, ny = sx + dx, sy + dy
        myd = 10**9
        opd = 10**9
        for rx, ry in resources:
            d1 = man(nx, ny, rx, ry)
            if d1 < myd:
                myd = d1
            d2 = man(ox, oy, rx, ry)
            if d2 < opd:
                opd = d2
        v = (-myd) + 0.5 * opd - 0.15 * man(nx, ny, ox, oy) + 0.3 * edge_bonus(nx, ny)
        if v > bestv:
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]