def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res_list = resources

    def cell_score(x, y):
        if not inb(x, y) or (x, y) in obst:
            return -10**9
        best = -10**9
        for rx, ry in res_list:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            cap = 2 if (x, y) == (rx, ry) else 0
            lead = do - ds  # positive means we are closer than opponent after move
            oppd = cheb(x, y, ox, oy)
            # Prefer taking now, then improving lead, then reducing our distance, then breaking ties deterministically
            key = (cap * 1000 + lead, -ds, -oppd, -(rx * 8 + ry))
            val = key[0] * 10**6 + key[1] * 10**3 + key[2]
            if (x, y) == (rx, ry):
                val += 10**7
            if val > best:
                best = val
        # Small bias: if we can't clearly win a resource, keep moving toward the closest one
        if best <= -10**8:
            mind = min(cheb(x, y, rx, ry) for rx, ry in res_list)
            best = -mind
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        val = cell_score(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]