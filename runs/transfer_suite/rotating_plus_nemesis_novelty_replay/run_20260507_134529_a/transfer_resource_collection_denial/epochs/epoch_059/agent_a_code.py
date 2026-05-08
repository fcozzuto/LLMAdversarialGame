def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v > best[0] or (v == best[0] and (nx, ny) < (best[1], best[2])):
                best = (v, nx, ny)
        return [best[1] - sx, best[2] - sy]

    best_score = -10**18
    best_move = (0, 0)

    # Evaluate moves by how much they improve our closest-resource access vs opponent's.
    # Tie-break: prefer smaller my distance to the contested target, then deterministic lexicographic move.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        my_min_d = 10**9
        opp_min_d = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            if myd < my_min_d:
                my_min_d = myd
            opd = cheb(ox, oy, rx, ry)
            if opd < opp_min_d:
                opp_min_d = opd

        # Primary: maximize (opponent access - our access). Secondary: get closer (min my_min_d).
        # Tertiary: reduce cheb distance to opponent slightly to avoid being cornered.
        my_to_opp = cheb(nx, ny, ox, oy)
        score = (opp_min_d - my_min_d) * 1000 - my_min_d * 2 - my_to_opp

        if (score > best_score) or (score == best_score and (my_min_d, my_to_opp, dx, dy) < (best_score, best_move[0], best_move[1], 0, 0)):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]