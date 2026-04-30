def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    resset = set((r[0], r[1]) for r in resources)
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obs_adj(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obs:
                    p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not moves:
        return [0, 0]

    if not resources:
        best, bestv = [0, 0], -10**9
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if blocked(nx, ny):
                continue
            v = kdist(nx, ny, ox, oy) - 0.7 * obs_adj(nx, ny)
            if v > bestv or (v == bestv and (mx, my) < tuple(best)):
                bestv = v
                best = [mx, my]
        return best

    best, bestv = [0, 0], -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if blocked(nx, ny):
            continue

        r_here = 1 if (nx, ny) in resset else 0
        d_me = 10**9
        d_op = 10**9
        best_gain = -10**18

        # Evaluate resources likely to be captured soon (cheap subset)
        for (rx, ry) in resources:
            dm = kdist(nx, ny, rx, ry)
            if dm > d_me:
                continue
            d_me = dm
        for (rx, ry) in resources:
            do = kdist(ox, oy, rx, ry)
            if do < d_op:
                d_op = do

        # Prefer moving toward nearest resource; discourage giving opponent earlier capture
        nearest_bonus = -0.9 * d_me
        steal_pen = 0.0
        if d_op != 10**9:
            # If we are slower than opponent to the best target, penalize strongly
            # (use current nearest estimate via d_me/d_op)
            delta = d_me - d_op
            if delta > 0:
                steal_pen = -2.5 * delta
            else:
                steal_pen = 1.2 * (-delta)

        # Prefer positions closer to board centers slightly (stability)
        cx, cy = (gw - 1) / 2.0, (gh - 1) / 2.0
        center = -0.05 * (abs(nx - cx) + abs(ny - cy))

        v = 8.0 * r_here + nearest_bonus + steal_pen + center - 0.6 * obs_adj(nx, ny)

        if v > bestv or (v == bestv and (mx, my) < tuple(best)):
            bestv = v
            best = [mx, my]
    return best