def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        best = (0, 0); bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Prefer moves that increase (opponent distance - self distance) to some resource;
    # tie-break by closer self distance and further from opponent.
    best = (0, 0); bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_r = -10**18
        self_min = 10**9
        opp_min = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            self_min = ds if ds < self_min else self_min
            opp_min = do if do < opp_min else opp_min
            gain = do - ds
            # Extra bias to pick a resource we can get very close to.
            val = gain * 4 - ds
            if val > best_r:
                best_r = val
        v = best_r + (cheb(nx, ny, ox, oy) * 0.05)  # slight survival / spacing bias
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]