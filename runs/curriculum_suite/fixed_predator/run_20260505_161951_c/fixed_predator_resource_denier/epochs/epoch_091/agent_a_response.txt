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
        home = (0, 0) if cheb(x, y, 0, 0) <= cheb(x, y, w-1, h-1) else (w-1, h-1)
        hx, hy = home
        best = (0, 0); bestv = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = -cheb(nx, ny, hx, hy) * 100 - cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best_lead = None; best_lead_v = -10**18
    opp_near = None; opp_near_d = 10**18
    for rx, ry in resources:
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        if lead > best_lead_v:
            best_lead_v = lead; best_lead = (rx, ry)
        if do < opp_near_d:
            opp_near_d = do; opp_near = (rx, ry)

    # If we can't get a clear lead, prioritize intercepting the resource closest to the opponent.
    target = best_lead if best_lead_v >= 1 else opp_near
    tx, ty = target

    # One-step heuristic: move to reduce distance to target while avoiding giving opponent a big advantage.
    best = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        ds_now = cheb(nx, ny, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        adv = do_now - ds_now
        # Additional tie-break: keep distance to opponent (denial pressure) and stay away from edges that trap.
        v = adv * 300 - ds_now * 2 - cheb(nx, ny, ox, oy) * 1
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]