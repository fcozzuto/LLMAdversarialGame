def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def occ(x, y):
        return (x, y) in obst

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def obstacle_pressure(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obst:
                    p += 1
        return p

    def target_value(px, py, rx, ry):
        ds = cheb(px, py, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets we can win or at least reach sooner; avoid ones where opponent is clearly closer.
        if do + 1 < ds:
            return -1000000 + do - ds  # abandon "lost" targets
        # Win pressure increases when we are closer.
        gap = do - ds  # positive means we are closer
        # Encourage picking a target that opponent can't reach "immediately".
        immediate_opp_pen = 0
        if do <= 1 and ds > do:
            immediate_opp_pen = 200
        # Mildly prefer nearer resources for both agents.
        closeness = ds
        return gap * 120 - immediate_opp_pen - closeness * 3 - obstacle_pressure(rx, ry) * 2

    best_move = (0, 0)
    best_score = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or occ(nx, ny):
            continue
        # Pick the best target after this move, but also discourage moves that step too near obstacles.
        local_best = -10**18
        for rx, ry in resources:
            if occ(rx, ry):
                continue
            val = target_value(nx, ny, rx, ry)
            if val > local_best:
                local_best = val
        # Small tie-break: prefer moves that reduce our distance to the overall best target we can see.
        tie = 0
        if local_best == -10**18:
            tie = -obstacle_pressure(nx, ny)
        else:
            # Approximate tie-break by maximizing gap for the closest currently (not opponent) reachable target.
            tie_best = -10**18
            for rx, ry in resources:
                if occ(rx, ry):
                    continue
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                if do <= ds + 1:
                    g = do - ds
                    if ds < 6:
                        t = g * 50 - ds * 2
                        if t > tie_best:
                            tie_best = t
            tie = tie_best
        score = local_best + tie - obstacle_pressure(nx, ny) * 6
        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]