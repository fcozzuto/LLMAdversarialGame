def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((a, b) for a, b in obstacles)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        tx, ty = w - 1, h - 1
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy) * 4 - (abs(nx - tx) + abs(ny - ty)) - cheb(nx, ny, 0, 0) * 0.1
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Pick a target with maximum "earlier arrival" advantage.
    best_target = resources[0]; best_tscore = -10**18
    for rx, ry in resources:
        d_self = cheb(x, y, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        tscore = (d_opp - d_self) * 10 - d_self * 0.2
        if tscore > best_tscore:
            best_tscore = tscore; best_target = [rx, ry]
    rx, ry = best_target

    # Choose the move that most increases our advantage to the chosen target and worsens theirs.
    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we are not advancing toward the target, penalize strongly.
        adv = (do - ds) * 12 - ds * 0.3
        # Deny: being closer to the target while staying farther from opponent reduces their blocking potential.
        deny = (cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)) * -2
        sep = cheb(nx, ny, ox, oy) * 0.05
        # Small preference for moving generally toward target.
        toward = - (abs(nx - rx) + abs(ny - ry)) * 0.05
        v = adv + deny + sep + toward
        if v > bestv:
            bestv = v; best = [dx, dy]
    return best