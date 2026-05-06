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
        tx, ty = w - 1, h - 1
        bx, by = 0, 0
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            # Go to our "home" while not letting opponent cut through us
            v = cheb(nx, ny, ox, oy) * 300 - (abs(nx - tx) + abs(ny - ty)) * 2 - cheb(nx, ny, bx, by) * 1
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Pick a resource that we can reach significantly earlier than opponent.
    best_res = resources[0]
    best_gain = -10**18
    for rx, ry in resources:
        d_ours = cheb(x, y, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # favor large advantage, but also some closeness to reduce pathing risk
        gain = (d_opp - d_ours) * 100 - d_ours
        if gain > best_gain:
            best_gain = gain; best_res = (rx, ry)

    tx, ty = best_res
    # One-step lookahead: choose move that improves our capture chance vs opp.
    cur_ours = cheb(x, y, tx, ty); cur_opp = cheb(ox, oy, tx, ty)
    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        d_ours2 = cheb(nx, ny, tx, ty)
        # Opponent likely also decreases their distance to the best remaining resource (approx).
        # Estimate by assuming opponent can move to reduce cheb by 1 if not already adjacent.
        d_opp2_est = cur_opp - 1 if cur_opp > 0 else 0
        our_improve = (cur_ours - d_ours2)
        opp_pressure = (d_opp2_est - d_ours2) - (cur_opp - cur_ours)
        # Mild obstacle proximity penalty to avoid jittering into walls
        adj_wall = 0
        for sx, sy in ((1,0),(-1,0),(0,1),(0,-1)):
            ax, ay = nx + sx, ny + sy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs:
                adj_wall += 1
        v = our_improve * 80 + opp_pressure * 60 - d_ours2 * 4 - adj_wall * 2
        # If we're moving directly onto any resource, boost strongly
        if (nx, ny) in obs:
            v -= 1000000
        for rx, ry in resources:
            if nx == rx and ny == ry:
                v += 2000
                break
        if v > bestv:
            bestv = v; best = [dx, dy]

    return best