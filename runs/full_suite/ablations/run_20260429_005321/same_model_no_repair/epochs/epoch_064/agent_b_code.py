def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        if not inb(x, y):
            return 10**7
        if (x, y) in obstacles:
            return 10**6
        p = 0
        for nx in (x - 1, x, x + 1):
            for ny in (y - 1, y, y + 1):
                if (nx, ny) in obstacles:
                    p += 2
        return p

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # Select a target resource: prefer ones we are closer to than the opponent
    if resources:
        best_r = resources[0]
        best_v = cheb(sx, sy, best_r[0], best_r[1]) - cheb(ox, oy, best_r[0], best_r[1])
        for rx, ry in resources[1:]:
            v = cheb(sx, sy, rx, ry) - cheb(ox, oy, rx, ry)
            if v < best_v or (v == best_v and (rx, ry) < (best_r[0], best_r[1])):
                best_v, best_r = v, (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose move that reduces our distance to target while not letting opponent get too close
    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        p = obs_pen(nx, ny)
        if p >= 10**6:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # If opponent can reach the target faster, avoid helping them by prolonging their advantage
        val = myd - 0.35 * (opd - cheb(ox, oy, tx, ty))  # keeps deterministic structure
        # More direct deterrent: prefer moves that don't make us significantly farther while opponent is near
        val += 0.15 * cheb(nx, ny, ox, oy)
        val += 0.9 * p
        # Slight preference for progress
        val += 0.02 * (cheb(nx, ny, tx, ty) - cheb(sx, sy, tx, ty))
        if val < best_score or (val == best_score and (dx, dy) < best_move):
            best_score, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]