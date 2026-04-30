def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = {(int(x), int(y)) for x, y in obstacles}
    res = [(int(x), int(y)) for x, y in resources]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                c += 1
        return c

    if not res:
        # No resources: keep distance from opponent and move away from obstacles.
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            v = 3 * cheb(nx, ny, ox, oy) - 0.7 * (abs(nx - (w//2)) + abs(ny - (h//2))) - 2.0 * near_obs(nx, ny)
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Choose contested target: maximize (opp_dist - my_dist).
    best_target = res[0]; best_gain = -10**18
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        gain = opd - myd
        if gain > best_gain:
            best_gain = gain; best_target = (rx, ry)

    tx, ty = best_target

    # Evaluate candidate move with resource competition and obstacle/edge control.
    best_move = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        my_to_t = cheb(nx, ny, tx, ty)
        opp_to_t = cheb(ox, oy, tx, ty)

        # Competition score across all resources: prefer moves that increase advantage.
        comp = 0
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            comp += (opd - myd)

        # Additional terms: prevent being edged in, and keep momentum toward target.
        center = abs(nx - (w//2)) + abs(ny - (h//2))
        v = 1.8 * comp + 2.2 * (opp_to_t - my_to_t) - 0.8 * center - 2.2 * near_obs(nx, ny)

        # If opponent is closer to target, prioritize moves that reduce our distance more than their distance.
        if best_gain < 0:
            v += 2.5 * (cheb(sx, sy, tx, ty) - my_to_t)

        if v > bestv:
            bestv = v; best_move = [dx, dy]

    return best_move