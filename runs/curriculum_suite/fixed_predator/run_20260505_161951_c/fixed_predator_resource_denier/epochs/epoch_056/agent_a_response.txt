def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if observation["turn_index"] % 2:
        dirs = [dirs[i] for i in [4, 5, 3, 6, 2, 7, 1, 8, 0]]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1, h - 1
        best = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 1000 + (nx - (w - 1 - tx)) - (abs(nx - tx) + abs(ny - ty)) * 2
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Evaluate each move by targeting the single best "swing" resource for us or deny one they are closer to.
    best = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        cur = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(nx, ny, ox, oy)  # proxy to discourage moves that give opponent immediate advantage elsewhere
            d_opp_to_r = cheb(ox, oy, rx, ry)
            # If we are closer to the resource than opponent, gain; if not, deny when they are close.
            rel = d_opp_to_r - ds
            if rel > 0:
                cur += rel * 120 - ds * 2
            else:
                # Deny: strongly prefer moving toward resources where opponent is currently closer than us.
                cur += rel * 30 - (-rel) * 2
            # Small preference to not step into opponent's near-control region
            cur += (cheb(nx, ny, ox, oy) - do) * 1
        # Secondary objective: stay away from obstacles already handled; use slight bias toward nearest resource to finish.
        # If multiple moves tie, prefer the one that increases distance from opponent (resource_denier discouragement).
        nearest_ds = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        tie = cheb(nx, ny, ox, oy)
        v = cur * 10 - nearest_ds - tie * 0.5
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]