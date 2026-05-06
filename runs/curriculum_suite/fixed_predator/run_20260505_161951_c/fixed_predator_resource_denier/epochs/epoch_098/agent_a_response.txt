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
    tx, ty = w - 1, h - 1  # home near our start corner
    if not resources:
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy) * 50 - (abs(nx - tx) + abs(ny - ty)) * 2
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Choose a resource: prioritize ones we can beat, else contest nearest.
    best_r = resources[0]; best_rv = -10**18
    for rx, ry in resources:
        d_self = cheb(x, y, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        beat = d_opp - d_self  # positive if we are earlier
        cont = -min(cheb(ox, oy, rx, ry), cheb(ox, oy, rx, ry))  # keep simple/deterministic
        rv = beat * 100 - d_self * 2 + cont * 0
        if rv > best_rv:
            best_rv = rv; best_r = [rx, ry]

    rx, ry = best_r
    # Evaluate our next step by immediate progress to target and denying opponent by reducing their advantage.
    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        d_self_n = cheb(nx, ny, rx, ry)
        d_opp_cur = cheb(ox, oy, rx, ry)
        gain = (d_opp_cur - d_self_n) * 120 - d_self_n * 3

        # If opponent is close to target, bias toward the line between us and the target to "intercept".
        opp_close = cheb(ox, oy, rx, ry)
        inter = 0
        if opp_close <= 2:
            # move toward the Chebyshev mid closer to opponent path
            mx = (ox + rx) // 2; my = (oy + ry) // 2
            inter = -cheb(nx, ny, mx, my) * 30

        # Mild obstacle/anti-crowding: keep away from opponent a bit to prevent easy steals.
        crowd = -cheb(nx, ny, ox, oy) * 1.5

        # If we can't improve much, drift to home after exhausting contest.
        fallback = -(abs(nx - tx) + abs(ny - ty)) * 0.3

        v = gain + inter + crowd + fallback
        if v > bestv:
            bestv = v; best = [dx, dy]
    return best