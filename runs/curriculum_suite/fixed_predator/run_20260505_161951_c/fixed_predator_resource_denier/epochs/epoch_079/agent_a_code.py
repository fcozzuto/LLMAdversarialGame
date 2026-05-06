def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = {(a, b) for a, b in obstacles}
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not resources:
        # Run to far corner while keeping distance from opponent
        tx, ty = w - 1, h - 1
        best, bestv = [0, 0], -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy) * 10 - (abs(nx - tx) + abs(ny - ty))
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    # Anticipatory denial: try to reach resources earlier; if trailing, move to cells that slow opponent.
    best, bestv = [0, 0], -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        my_near, opp_near = 10**9, 10**9
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            if my_d < my_near: my_near = my_d
            opp_d = cheb(ox, oy, rx, ry)
            if opp_d < opp_near: opp_near = opp_d
        # After our move, opponent might also advance: approximate by allowing them to reduce cheb by 1 if unblocked.
        # This is a coarse deterministic hedge: prefer moves that keep our advantage even under 1-step opponent progress.
        opp_advantage = opp_near - (my_near - 1)
        my_advantage = opp_near - my_near
        # Also penalize moving adjacent to an immediate contested resource to avoid getting "denied" next step.
        adj_contest = 0
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) <= 1 and cheb(ox, oy, rx, ry) <= 1:
                adj_contest += 1
        v = (my_advantage * 120) + (opp_advantage * 30) + cheb(nx, ny, ox, oy) * 2 - adj_contest * 25
        if v > bestv:
            bestv, best = v, [dx, dy]
    return best