def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    i_am_pursuer = ("pursuer" in roles) or ("evader" not in roles)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x, y, tx, ty):
        dx = abs(tx - x); dy = abs(ty - y)
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not i_am_pursuer:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        target = max(corners, key=lambda c: cheb(sx, sy, c[0], c[1]) + 0.1 * (abs(c[0]-ox) + abs(c[1]-oy)))
        best = (0, 0); bestd = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, ox, oy)
                if d > bestd or (d == bestd and (dx, dy) < best):
                    bestd = d; best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Predict evader next step toward a corner that maximizes distance from us
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
    # Evaluate opponent candidate moves: prefer moving toward chosen corner, while increasing distance from us
    opp_best = (0, 0); opp_score = None; opp_dist = -1
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if valid(nx, ny):
            toward = -cheb(nx, ny, best_corner[0], best_corner[1])
            inc = cheb(nx, ny, sx, sy)
            sc = (inc, toward, -abs(nx - best_corner[0]) - abs(ny - best_corner[1]))
            if opp_score is None or sc > opp_score or (sc == opp_score and (dx, dy) < opp_best):
                opp_score = sc; opp_best = (dx, dy); opp_dist = inc
    px, py = ox + opp_best[0], oy + opp_best[1]

    # Chase predicted position with obstacle-aware greedy (Chebyshev)
    best = (0, 0); bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            d = cheb(nx, ny, px, py)
            if bestd is None or d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d; best = (dx, dy)
    return [int(best[0]), int(best[1])]