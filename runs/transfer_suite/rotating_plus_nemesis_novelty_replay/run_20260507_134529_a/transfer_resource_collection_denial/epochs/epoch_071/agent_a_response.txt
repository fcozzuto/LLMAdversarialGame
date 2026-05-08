def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            # head toward opponent to cut off later routes
            v = -max(abs(nx - ox), abs(ny - oy))
            cand = (v, abs(nx - ox) + abs(ny - oy), dx, dy, nx, ny)
            if best is None or cand < best:
                best = cand
        return [best[2], best[3]]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # We act to secure the most "contested" resource:
    # maximize (opp_access - my_access), where access is Chebyshev distance.
    # Also slightly prefer moves that reduce my access to that contested target.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        # pick contested target from this hypothetical position
        best_gain = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # primary: how much earlier we can reach than opponent
            gain = opp_d - my_d
            # secondary: how fast we reach among equally contested targets
            cand_t = (-gain, my_d, rx, ry)  # reversed for min
            if best_gain is None or cand_t < best_gain:
                best_gain = cand_t

        gain = -best_gain[0]
        my_to_target = best_gain[1]
        # extra: deny by preferring moves that increase opponent distance to the nearest resource
        opp_nearest = None
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            if opp_nearest is None or d < opp_nearest:
                opp_nearest = d

        # score higher is better; convert to minimization tuple
        # (invert gain, then prefer smaller my_to_target, then lexicographic move)
        score = (-gain, my_to_target, dx, dy)
        if best is None or score < best:
            best = score

    return [best[2], best[3]]