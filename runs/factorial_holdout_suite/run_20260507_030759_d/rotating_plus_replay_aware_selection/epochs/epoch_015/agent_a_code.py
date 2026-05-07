def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def cell_value(x, y):
        best = (-10**18, 10**18)
        for rx, ry in resources:
            ds = man(x, y, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds == 0 and (x, y) == (rx, ry):
                return (10**12, 0)
            adv = do - ds
            # Prefer cells that are closer than opponent, but also overall progress
            v = adv * 300 - ds * 7
            # Small tie-break: prefer resources that are nearer to us (lower ds)
            if v > best[0] or (v == best[0] and ds < best[1]):
                best = (v, ds)
        return best

    best_move = [0, 0]
    best = (-10**18, 10**18)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        v, ds = cell_value(nx, ny)
        # Favor faster immediate capture, then best value, then lower self distance
        if v > best[0] or (v == best[0] and ds < best[1]) or (v == best[0] and ds == best[1] and (mx, my) < (best_move[0], best_move[1])):
            best = (v, ds)
            best_move = [mx, my]

    return best_move