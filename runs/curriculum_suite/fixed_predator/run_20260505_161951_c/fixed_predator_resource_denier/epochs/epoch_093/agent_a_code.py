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
        # Fall back to staying near our corner while making it hard for opponent to cut
        home = (0, 0) if (x <= w//2 and y <= h//2) else (w-1, h-1)
        best = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x+dx, y+dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy) * 5 - cheb(nx, ny, home[0], home[1]) * 2
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Choose a resource we are meaningfully closer to; otherwise shift to denial around the opponent's likely target.
    best_gain = -10**18
    target = resources[0]
    for rx, ry in resources:
        d_ours = cheb(x, y, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        gain = (d_opp - d_ours) * 10 - (d_ours) * 0.5
        if gain > best_gain:
            best_gain = gain; target = (rx, ry)

    # If not ahead, deny: move to improve our distance to opponent's closest resource more than theirs.
    if best_gain <= 0:
        bestv = -10**18
        opp_target = resources[0]
        for rx, ry in resources:
            v = -cheb(ox, oy, rx, ry)
            if v > bestv:
                bestv = v; opp_target = (rx, ry)
        target = opp_target

    tx, ty = target
    best = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x+dx, y+dy
        if not valid(nx, ny):
            continue
        d_ours = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Prefer steps that get us closer while not giving opponent an easier path to the same target.
        # Also slightly prefer increasing opponent distance to our current/target vicinity.
        v = (d_opp - d_ours) * 12 - d_ours * 0.8 + cheb(nx, ny, ox, oy) * 0.6
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]