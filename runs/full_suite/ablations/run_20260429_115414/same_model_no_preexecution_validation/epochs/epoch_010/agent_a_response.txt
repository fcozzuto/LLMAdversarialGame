def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set

    # Target selection: resource we can win the race to (by Chebyshev distance)
    best_r = None
    best_val = -10**9
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd) * 100 - sd
        if best_r is None or val > best_val or (val == best_val and (rx, ry) < best_r):
            best_val = val
            best_r = (rx, ry)

    if best_r is None:
        target = (ox, oy)  # fallback: interact with opponent
    else:
        target = best_r

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    def min_obs_dist(x, y):
        if not obstacles:
            return 10**9
        m = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, int(ax), int(ay))
            if d < m:
                m = d
                if m == 0:
                    break
        return m

    # Move scoring
    tx, ty = target
    opp_d = cheb(sx, sy, ox, oy)
    prefer_hold = 1 if opp_d <= 2 else 0
    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in legal_moves:
        sd = cheb(nx, ny, tx, ty)
        # Obstacle influence
        od = min_obs_dist(nx, ny)
        obst_pen = 0
        if od == 0:
            obst_pen = 10**9
        elif od == 1:
            obst_pen = 120
        elif od == 2:
            obst_pen = 35
        elif od == 3:
            obst_pen = 10

        # Race-advantage shift (also helps choose good routes)
        if resources:
            # Approx compute against current best target only; also nudge away from losing race
            my_adv = (cheb(ox, oy, tx, ty) - sd)
        else:
            my_adv = 0

        # Opponent pressure: if close, avoid giving them the same resource by reducing their distance
        nd_opp = cheb(nx, ny, ox, oy)
        opp_term = 0
        if prefer_hold:
            opp_term = (opp_d - nd_opp) * 6  # tend to stay or move to keep parity
        else:
            opp_term = -nd_opp * 0.2  # light deterrent from straying too far

        # Small tie-break to keep deterministic "grid-walk" towards increasing x then y
        tie = (nx * 0.01 + ny * 0.001)

        score = (-sd * 1000) + my_adv * 120 + opp_term + tie - obst_pen
        if best_move is None or score > best_score