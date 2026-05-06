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

    def best_goal_dir(tx, ty):
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            d_goal = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            v = (d_opp * 2) - d_goal
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    if not resources:
        return best_goal_dir(w - 1, h - 1)

    # Pick a resource where we are relatively closer than the opponent, breaking ties by closeness.
    best_res = None; best_res_v = -10**18
    for rx, ry in resources:
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        v = (do - ds) * 120 - ds
        if v > best_res_v:
            best_res_v = v; best_res = (rx, ry)

    tx, ty = best_res
    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        ds_new = cheb(nx, ny, tx, ty)
        # Anticipate opponent pressure: approximate their next move reducing cheb to target by 1 if not blocked.
        do_now = cheb(ox, oy, tx, ty)
        do_new = do_now - (1 if do_now > 0 else 0)
        v = (do_new - ds_new) * 160 - ds_new
        if (nx, ny) == (tx, ty):
            v += 10**6
        if v > bestv:
            bestv = v; best = [dx, dy]
    return best