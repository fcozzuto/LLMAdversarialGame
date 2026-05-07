def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    # Collect immediately if possible
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2; ax = -ax if ax < 0 else ax
        ay = y1 - y2; ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay

    if not res_list:
        # Drift toward opponent corner direction
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best = (0, 0, 10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[2]:
                best = (dx, dy, d)
        return [best[0], best[1]]

    # Choose opponent's likely resource (the one they are closest to right now)
    opp_best = None; opp_dd = 10**9
    for rx, ry in res_list:
        d = cheb(ox, oy, rx, ry)
        if d < opp_dd or (d == opp_dd and (rx+ry) < (opp_best[0]+opp_best[1])):
            opp_dd = d; opp_best = (rx, ry)
    deny_cell = (opp_best[0], opp_best[1])

    my_target = None; my_margin = -10**9; my_dist = 10**9
    for rx, ry in res_list:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        margin = opd - myd  # positive if we are closer
        # prioritize winning resources, then reduce our distance
        if margin > my_margin or (margin == my_margin and (myd < my_dist)):
            my_margin = margin; my_dist = myd; my_target = (rx, ry)

    # If we aren't clearly ahead anywhere, deny opponent's likely target by heading there/adjacent
    if my_margin <= 0:
        tx, ty = deny_cell
        mode = 1
    else:
        tx, ty = my_target
        mode = 0

    # Second-step decision: also consider scoring swing vs opponent after the move
    best = None; best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if mode == 1:
            d_me = cheb(nx, ny, tx, ty)
            # keep opponent farther from deny cell while still approaching it
            d_op = cheb(ox, oy, tx, ty)
            val = -(d_me) + 0.15 * (d_op - d_me)
        else:
            # choose move that maximizes immediate advantage over opponent for our chosen target
            d_me = cheb(nx, ny, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            val = (d_op - d_me) * 10 - d_me
        # tie-break: prefer moves that don't step into "dead" spots far from any resource
        if best is None or val > best_val:
            best_val = val; best = (dx, dy)

    return [int(best[0]), int(best[1])]