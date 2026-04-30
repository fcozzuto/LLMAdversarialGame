def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    # Choose our target deterministically by "advantage"
    if resources:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            # Prefer large adv, then closer to us, then lexicographic by position
            key = (-adv, myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (W - 1) // 2, (H - 1) // 2

    # Opponent target estimate: nearest resource to them (tie by lexicographic)
    if resources:
        o_best = None
        for rx, ry in resources:
            opd = cheb(ox, oy, rx, ry)
            key = (opd, rx, ry)
            if o_best is None or key < o_best[0]:
                o_best = (key, rx, ry)
        otx, oty = o_best[1], o_best[2]
    else:
        otx, oty = (W - 1) // 2, (H - 1) // 2

    def penalty_near_obstacle(x, y):
        # Penalize proximity to obstacles; strong if stepping onto one
        if (x, y) in obstacles:
            return 1000
        p = 0
        for (ox2, oy2) in obstacles:
            d = cheb(x, y, ox2, oy2)
            if d == 0:
                return 1000
            if d == 1: p += 12
            elif d == 2: p += 4
        return p

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # If engine rejects, we'd stay; discourage by simulation score anyway
        if (nx, ny) in obstacles:
            myd = cheb(sx, sy, tx, ty)
            opd = cheb(ox, oy, otx, oty)
            val = -10**12 - penalty_near_obstacle(nx, ny) - myd + opd
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
            continue

        my_to_t = cheb(nx, ny, tx, ty)
        op_to_o = cheb(ox, oy, otx, oty)

        # Opponent "pressures": resources they are currently closer to than us
        # Reward moves that increase that gap for the best competing resource.
        comp_gap = 0
        if resources:
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                gap = opd - myd  # positive => they are farther from it than we are
                if gap < 0:
                    # If we are worse at a resource, penalize proportionally
                    comp_gap += gap
        # So comp_gap is negative or 0; higher is better (closer to 0)
        my_near = 0
        if resources:
            m = 10**9