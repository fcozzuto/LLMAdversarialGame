def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((a, b) for a, b in obstacles)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy) * 10 - (abs(nx - (w - 1)) + abs(ny - (h - 1))) * 0.1
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Evaluate candidate move by "resource tempo" plus a mild denial pressure if opponent is closer.
    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        v = 0.0
        for rx, ry in resources:
            d0 = cheb(nx, ny, rx, ry)
            d1 = cheb(ox, oy, rx, ry)
            delta = d1 - d0  # positive if we are earlier
            # primary: chase earliest + strong denial if opponent is about to take it
            v += (delta * 30.0 - d0 * 1.2)
            if delta < 0:
                v += (-delta) * 10.0  # deny priority: reduce worst lateness
        # additional tie-breakers: don't step into "obvious" pursuit lanes
        v += cheb(nx, ny, ox, oy) * 2.0
        v -= abs(nx - ox) * 0.05 + abs(ny - oy) * 0.05
        if v > bestv:
            bestv = v; best = [dx, dy]
    return best