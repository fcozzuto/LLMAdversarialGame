def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def step_score(x, y):
        if (x, y) in obst:
            return -10**9
        best = -10**18
        # Deterministic resource ordering for tie breaks
        for rx, ry in sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1])):
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            cap = 3.0 if (x, y) == (rx, ry) else 0.0
            lead = do - ds  # positive means we can reach sooner
            # Opportunistic, resource-denial oriented: prefer big lead; slight preference for low distance
            val = cap + 2.4 * lead - 0.45 * ds + 0.06 * cheb(x, y, ox, oy)
            if val > best:
                best = val
        # Extra small tie-break: keep closer to opponent early (denial), but avoid getting stuck
        best += -0.02 * cheb(x, y, ox, oy)
        return best

    # Small deterministic "strategic switch" when not improving: if opponent is much closer to all resources,
    # move toward the single nearest resource (to avoid deadlock).
    opp_best = -10**18
    best_res = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d > opp_best:
            opp_best = -d
            best_res = (rx, ry)
    # Compare our closest vs opponent closest to gauge contest
    my_min = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
    opp_min = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
    force_greed = my_min > opp_min + 1

    if force_greed and best_res is not None:
        tx, ty = best_res
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            return [dx, dy]

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            v = -10**9
        else:
            v = step_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move