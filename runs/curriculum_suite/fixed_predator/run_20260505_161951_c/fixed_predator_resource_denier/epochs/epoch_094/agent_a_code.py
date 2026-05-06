def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
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
        # deterministic "return to corner" while avoiding obstacles
        tx, ty = 0, 0
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, tx, ty) * -10 - cheb(nx, ny, ox, oy) * 1
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # pick target: win if we can arrive earlier; otherwise race
    best_r = None
    best_margin = -10**18
    best_opp_fast = -10**18
    for rx, ry in resources:
        d_s = cheb(x, y, rx, ry)
        d_o = cheb(ox, oy, rx, ry)
        margin = d_o - d_s
        if d_o <= 1:
            # if opponent is essentially on top of a resource, we must contest it
            opp_fast = 10**6 - d_s
            if opp_fast > best_opp_fast:
                best_opp_fast = opp_fast; best_r = (rx, ry)
        if margin > best_margin or (margin == best_margin and (best_r is None or (d_s < cheb(x, y, best_r[0], best_r[1])))):
            best_margin = margin; best_r = (rx, ry)

    rx, ry = best_r
    # one-step greedy: minimize distance to target; also prefer positions that increase our margin over opponent
    best_move = [0, 0]; best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        d_s2 = cheb(nx, ny, rx, ry)
        d_o2 = cheb(ox, oy, rx, ry)
        margin2 = d_o2 - d_s2
        score = margin2 * 1000 - d_s2 * 3
        # extra tie-break: avoid getting closer to opponent if we're not winning the contested target
        if margin2 <= 0:
            score -= cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score = score; best_move = [dx, dy]
    return best_move