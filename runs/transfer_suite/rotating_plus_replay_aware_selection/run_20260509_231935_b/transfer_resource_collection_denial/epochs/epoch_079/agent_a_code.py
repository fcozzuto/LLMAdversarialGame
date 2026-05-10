def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best_move = [0, 0]
    best_val = -10**18

    # Precompute which resources opponent is threatening more than us (static per turn)
    opp_pref = set()
    for rx, ry in res:
        d_s = cheb(sx, sy, rx, ry)
        d_o = cheb(ox, oy, rx, ry)
        if d_o + 1 < d_s:
            opp_pref.add((rx, ry))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_best = 10**9
        opp_best = 10**9
        # Evaluate top target considering race with opponent
        for rx, ry in res:
            d_m = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            my_best = d_m if d_m < my_best else my_best
            opp_best = d_o if d_o < opp_best else opp_best

        # Score: prefer small distance to a resource we can likely take first.
        # Penalize getting too close to opponent's nearest resources.
        race_w = 0.0
        for rx, ry in res:
            d_m = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            if d_o + 1 < d_m:
                race_w -= 2.5
            else:
                race_w += 1.0 / (1 + d_m)

        # Strong preference for best reachable resource, plus mild center bias to avoid dead ends
        center_bias = -0.05 * cheb(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0)
        # Safety bias: avoid moving next to obstacles if tied
        wall_safety = 0
        for ax, ay in [(nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1), (nx+1, ny+1), (nx+1, ny-1), (nx-1, ny+1), (nx-1, ny-1)]:
            if (ax, ay) in obs:
                wall_safety -= 0.2

        # Tie-break deterministically by move order already in dirs
        val = -1.2 * my_best + 0.15 * opp_best + race_w + center_bias + wall_safety
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move