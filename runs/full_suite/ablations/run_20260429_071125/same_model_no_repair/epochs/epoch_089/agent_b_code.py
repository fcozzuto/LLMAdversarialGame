def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dist_to_nearest_obstacle(x, y):
        if not obstacles:
            return 999
        best = 999
        for (ax, ay) in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best

    # Choose a materially different priority: resources we're "more likely" to reach first.
    best_target = resources[0]
    best_margin = -10**9
    for (rx, ry) in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        margin = opd - myd  # positive means we're closer or equal
        # Slight bias toward closer resources to speed up collection.
        margin2 = margin * 10 - myd
        if margin2 > best_margin:
            best_margin = margin2
            best_target = (rx, ry)

    rx, ry = best_target

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        myd = cheb(nx, ny, rx, ry)
        opd = cheb(nx, ny, ox, oy)

        dObs = dist_to_nearest_obstacle(nx, ny)
        obstacle_pen = 0
        if dObs <= 0:
            obstacle_pen = 10**6
        else:
            obstacle_pen = (3 - dObs) * 4 if dObs < 3 else 0

        # If opponent is already adjacent to the target, value blocking/tempo: increase their distance.
        opp_adj = 1 if cheb(ox, oy, rx, ry) <= 1 else 0

        val = 0
        val += -myd * 20
        val += (opd * -1)  # we prefer not to get too close to opponent, reducing contest brawls
        val += (opd * -1) * (1 if cheb(nx, ny, ox, oy) <= 2 else 0)
        val += opp_adj * (opd)  # when target is threatened, move to increase opponent distance from this area
        val -= obstacle_pen

        # Deterministic tie-break: prefer lexicographically smaller move deltas.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]