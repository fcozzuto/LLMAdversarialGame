def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}
    res = [(int(p[0]), int(p[1])) for p in resources]
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs: c += 1
        return c
    best_move = (0, 0)
    best_val = -10**18

    if not res:
        # Move to farthest corner from opponent while avoiding obstacles
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        tx, ty = corners[0]
        far = -1
        for cx, cy in corners:
            d = cheb(cx, cy, ox, oy)
            if d > far: far = d; tx, ty = cx, cy
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): continue
            val = cheb(nx, ny, tx, ty) * -1 - 2 * near_obs(nx, ny)
            # mild separation from opponent
            val += cheb(nx, ny, ox, oy) * 0.25
            if val > best_val:
                best_val = val; best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose resource where we gain most over opponent (my_dist smaller than opp_dist)
    # With ties, prefer nearer resources and those further from opponent after their next move.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): continue
        my_best = 10**18
        tie_best = (10**18, 10**18, 10**18)
        for rx, ry in res:
            my_d = cheb(nx, ny, rx, ry)
            if my_d > my_best: continue
            opp_d = cheb(ox, oy, rx, ry)
            # encourage cutting off: maximize (opp_d - my_d), tie-break by closeness
            gain = opp_d - my_d
            after = 0
            # small bias to resources that are not adjacent to obstacles (smoother path)
            after = -0.5 * near_obs(rx, ry)
            key = (-gain, my_d, -opp_d, after)
            if key < tie_best:
                tie_best = key; my_best = my_d
        # recompute chosen target features from key
        # tie_best[0] = -gain, so gain = -tie_best[0]
        gain = -tie_best[0]
        my_d = tie_best[1]
        opp_d = -tie_best[2]
        val = gain * 10 + (-my_d) * 1.2 + (-near_obs(nx, ny)) * 2.0
        # avoid moving into opponent proximity unless it wins a resource race
        val += cheb(nx, ny, ox, oy) * 0.05
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val; best_move = (dx, dy)

    if best_move == (0, 0):
        # If every move blocked, stay
        return [0, 0]
    return [best_move[0], best_move[1]]