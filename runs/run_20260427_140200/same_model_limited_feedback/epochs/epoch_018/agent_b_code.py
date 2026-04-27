def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obst = set((p[0], p[1]) for p in obstacles)
    dxs = (-1, 0, 1)
    moves = [(dx, dy) for dx in dxs for dy in dxs]
    def clamp(x, y):
        if x < 0: x = 0
        if y < 0: y = 0
        if x >= w: x = w - 1
        if y >= h: y = h - 1
        return x, y
    def cheb(a, b, c, d):
        ax = a - c
        ay = b - d
        ax = -ax if ax < 0 else ax
        ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay
    opp_best = 10**9
    for r in resources:
        opp_best = min(opp_best, cheb(ox, oy, r[0], r[1]))
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obst:
            continue
        if resources:
            val = 0.0
            d_opp = 0
            for r in resources:
                ds = cheb(nx, ny, r[0], r[1])
                do = cheb(ox, oy, r[0], r[1])
                if ds == 0:
                    val += 1000.0
                    continue
                steal = 1.0 if ds <= do else 0.0
                val += steal * (50.0 / (ds + 1.0)) + (1.5 / (ds + 1.0)) * (1.0 - steal)
            # Avoid giving opponent easy access (prefer increasing their nearest resource distance)
            cur_opp = opp_best if opp_best < 10**9 else cheb(ox, oy, nx, ny)
            new_opp = min(cheb(ox, oy, r[0], r[1]) for r in resources) if resources else cur_opp
            val += (cur_opp - new_opp) * 3.0
        else:
            val = 0.0
        # Keep some pressure toward center to reduce tie loops
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        val += -0.05 * dist_center
        # Slightly penalize moving closer to opponent (prevents accidental collisions that help them)
        val += -0.2 / (cheb(nx, ny, ox, oy) + 1.0)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]