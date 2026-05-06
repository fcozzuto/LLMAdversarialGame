def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]; bestv = -10**9
        tx, ty = w - 1, h - 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy) - 0.2 * (abs(nx - tx) + abs(ny - ty))
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Choose the resource where we are relatively closest vs opponent (one-step metric).
    # Then choose our move to best improve this advantage immediately.
    best_target = None; best_t = -10**18
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer being closer, but also slightly prefer smaller absolute distances to avoid wandering.
        t = (od - sd) * 1000 - (sd + 0.25 * od)
        if t > best_t:
            best_t = t; best_target = (rx, ry)

    rx, ry = best_target
    # Our move score: decrease our distance and increase opponent's distance to that target.
    best = [0, 0]; bestv = -10**18
    our_prev = cheb(x, y, rx, ry); opp_prev = cheb(ox, oy, rx, ry)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        our_d = cheb(nx, ny, rx, ry)
        # Predict opponent's likely move next toward same target (greedy by our metric).
        # We only need the resulting cheb distance, not full simulation.
        opp_best_d = 10**9
        for odx, ody in dirs:
            nox, noy = ox + odx, oy + ody
            if not valid(nox, noy):
                continue
            d = cheb(nox, noy, rx, ry)
            if d < opp_best_d:
                opp_best_d = d
        # If opponent can't move (all blocked), keep their current distance.
        if opp_best_d == 10**9:
            opp_best_d = opp_prev

        v = (opp_best_d - our_d) * 10 + (our_prev - our_d) * 3 + (opp_prev - opp_best_d) * (-1)
        # Deterministic tie-break: prefer diagonal moves, then staying still (fixed order already).
        if v > bestv:
            bestv = v; best = [dx, dy]

    return best