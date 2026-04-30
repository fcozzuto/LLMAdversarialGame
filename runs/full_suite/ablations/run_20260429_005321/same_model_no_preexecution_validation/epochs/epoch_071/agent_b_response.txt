def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(x), int(y)) for x, y in obstacles}
    res = [(int(x), int(y)) for x, y in resources]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obs:
                c += 1
        return c

    # Deterministic target preference: resources where we reduce our distance faster than opponent.
    # If no resources, just drift away from opponent while avoiding obstacles.
    if not res:
        best = [0, 0]; bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            v = 1.2 * cheb(nx, ny, ox, oy) - 0.6 * near_obs(nx, ny)
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Evaluate the best resource we could "claim" from the next position.
        vbest = -10**18
        no = near_obs(nx, ny)
        dist_opp = cheb(nx, ny, ox, oy)

        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Lead in reaching that resource.
            lead = opd - myd  # positive means we are closer
            # Encourage closer-but-not-instantly-losing to opponent.
            claim = 2.0 * lead - 0.25 * myd
            # Slightly prefer resources not adjacent to obstacles.
            ro = near_obs(rx, ry)
            claim -= 0.15 * ro
            # Defensive coupling: if lead is small, keep distance from opponent.
            claim -= 0.05 * (1 if lead < 1 else 0) * (8 - min(8, dist_opp))
            if claim > vbest:
                vbest = claim

        # Global move modifiers: obstacle avoidance and staying away from opponent when no strong claim.
        v = vbest + 0.35 * dist_opp - 0.55 * no
        if v > bestv:
            bestv = v; best = [dx, dy]
    return best