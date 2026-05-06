def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def sd(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    obs_list = list(obstacles)

    def nearest_obs2(x, y):
        if not obs_list: return 999999
        m = None
        for ax, ay in obs_list:
            d = sd(x, y, ax, ay)
            if m is None or d < m: m = d
        return m if m is not None else 999999

    # Pick a target resource we can reach sooner than the opponent; otherwise drift to opponent side.
    if resources:
        best_res = None
        for rx, ry in resources:
            self_d = sd(sx, sy, rx, ry)
            opp_d = sd(ox, oy, rx, ry)
            margin = opp_d - self_d
            key = (margin, -self_d, rx, ry)
            if best_res is None or key > best_res[0]:
                best_res = (key, (rx, ry))
        tx, ty = best_res[1]
    else:
        tx, ty = (ox, oy)  # last resort: contest near opponent

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            val = -10**18
        elif (nx, ny) in obstacles:
            val = -10**18
        else:
            d_to_t = sd(nx, ny, tx, ty)
            d_to_o = sd(nx, ny, ox, oy)
            nobs2 = nearest_obs2(nx, ny)
            # Prefer approaching target, keep distance from opponent (denier), avoid obstacles.
            val = -d_to_t + 0.02 * d_to_o - (0.15 / (1 + nobs2))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move