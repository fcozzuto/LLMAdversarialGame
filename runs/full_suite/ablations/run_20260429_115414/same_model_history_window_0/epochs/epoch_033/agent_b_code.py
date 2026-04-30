def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]

    obst = set((p[0], p[1]) for p in obstacles)
    res = set((p[0], p[1]) for p in resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dsq(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if not res:
        return [0, 0]

    candidates = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = -10**18
    best_move = [0, 0]

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        best_self = 10**18
        best_opp = 10**18
        for rx, ry in res:
            if (rx, ry) in obst:
                continue
            d1 = dsq(nx, ny, rx, ry)
            if d1 < best_self:
                best_self = d1
            d2 = dsq(ox, oy, rx, ry)
            if d2 < best_opp:
                best_opp = d2

        v = (best_opp - best_self) - 0.001 * best_self + (0.05 if (nx, ny) in res else 0.0)
        if v > best:
            best = v
            best_move = [dx, dy]

    return best_move