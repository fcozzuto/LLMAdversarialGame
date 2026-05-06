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
        # Drift to a safe corner (farthest from opponent) with obstacle-avoidance.
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        home = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        bestm = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy) - cheb(nx, ny, home[0], home[1]) * 0.1
            if v > bestv:
                bestv = v; bestm = [dx, dy]
        return bestm

    # Resource-denial heuristic: choose move that maximizes our lead over opponent.
    # If we can’t win a resource lead, pick the move that reduces opponent advantage most.
    bestm = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        best_adv = -10**18
        best_dist = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_adv or (adv == best_adv and ds < best_dist):
                best_adv = adv; best_dist = ds
        # Small tie-breaks: go more directly toward the best resource; mildly avoid moving away from center.
        center_bias = 0
        cx = (w - 1) / 2.0; cy = (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        v = best_adv * 1000 - best_dist * 5 - dist_center * 0.1
        if v > bestv:
            bestv = v; bestm = [dx, dy]
    return bestm