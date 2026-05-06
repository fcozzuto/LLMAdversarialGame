def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(nx, ny): return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    home = (w - 1, h - 1) if (x, y) == (0, 0) else (0, 0)

    if not resources:
        best = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, home[0], home[1]) * -1 - cheb(nx, ny, ox, oy) * 0.05
            if v > bestv: bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best_rx, best_ry = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        ours = cheb(x, y, rx, ry)
        opp = cheb(ox, oy, rx, ry)
        # prefer targets where we have a real timing edge; otherwise still choose the best overall
        s = (opp - ours) * 10 - ours * 1 + (opp < ours) * (-6)
        if s > best_score:
            best_score = s; best_rx, best_ry = rx, ry

    target = (best_rx, best_ry)
    best = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny): 
            continue
        self_d = cheb(nx, ny, target[0], target[1])
        opp_d = cheb(ox, oy, target[0], target[1])
        # if opponent is close to the target, prioritize moving in a way that increases our chances and denies theirs
        v = (opp_d - self_d) * 8 - self_d * 2
        # slight repulsion from opponent to reduce instant denial collisions
        v += -cheb(nx, ny, ox, oy) * 0.25
        # bonus for moving closer to target specifically (ties)
        v += -(abs(nx - target[0]) + abs(ny - target[1])) * 0.01
        if v > bestv:
            bestv = v; best = (dx, dy)

    return [best[0], best[1]]