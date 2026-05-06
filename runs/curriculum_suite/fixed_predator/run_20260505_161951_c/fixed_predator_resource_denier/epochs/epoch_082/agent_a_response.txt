def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, head to opposite corner while minimizing collision risk.
    if not resources:
        tx, ty = w - 1, h - 1
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_goal = cheb(nx, ny, tx, ty)
            v = d_opp - d_goal
            if v > bestv or (v == bestv and (abs(dx)+abs(dy) < abs(best[0])+abs(best[1]))):
                bestv = v; best = [dx, dy]
        return best

    # Choose a "race-positive" target: where we are relatively closer than opponent.
    # Prefer higher (opp_dist - self_dist). Tie-break by smaller self_dist.
    best_target = None; best_key = None
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd)  # maximize; second term prefers smaller sd
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # One-step evaluation to avoid getting stuck behind obstacles and to handle denials.
    # Landing on a resource is strongly preferred.
    best_move = [0, 0]; bestv = -10**18
    resset = set((a, b) for a, b in resources)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        landed = 1 if (nx, ny) in resset else 0
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        # Move should both reduce our distance and increase our lead.
        v = landed * 10000 + (od - sd) * 50 - sd
        # Small tie-break: keep moving in roughly toward target.
        if v > bestv:
            bestv = v; best_move = [dx, dy]
    return best_move