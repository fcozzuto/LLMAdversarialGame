def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def obst_pen(x, y):
        p = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + ddx, y + ddy) in obst:
                p += 1
        return p

    def count_block(x, y):
        # Prefer squares that reduce opponent approach routes by being surrounded by obstacles.
        return obst_pen(x, y)

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If no resources, drift toward area that is far from opponent (material change vs previous resource-less logic).
    if not resources:
        # Choose among legal moves: maximize minimum distance to opponent corners (deterministic).
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = 0
            for cx, cy in corners:
                d = manh(nx, ny, cx, cy)
                d2 = manh(ox, oy, cx, cy)
                v += (d - d2)
            v -= count_block(nx, ny) * 0.3
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Resource contest heuristic: try to be the first to the most "swingy" resource.
    # Score a move by: (best self advantage on resources) - (risk of immediate opponent capture) + small safety terms.
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in legal:
        # Self's advantage on closest contested resource
        best_adv = None
        best_r = None
        for rx, ry in resources:
            ds = manh(nx, ny, rx, ry)
            do = manh(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer than opponent to that resource
            if best_adv is None or adv > best_adv or (adv == best_adv and ds < manh(nx, ny, best_r[0], best_r[1])):
                best_adv = adv
                best_r = (rx, ry)

        # Opponent immediate capture risk: estimate if they can reach the same best resource in <= we can.
        risk = 0
        if best_r is not None:
            rx, ry = best_r
            ds = manh(nx, ny, rx, ry)
            do = manh(ox, oy, rx, ry)
            risk = 1 if do <= ds else 0

        # Also consider moving closer to the nearest resource outright.
        nearest_self = None
        for rx, ry in resources:
            d = manh(nx, ny, rx, ry)
            if nearest_self is None or d < nearest_self:
                nearest_self = d

        # Small penalty for getting stuck near obstacles.
        s = best_adv * 10 - risk * 8 - nearest_self * 0.6 - count_block(nx, ny) * 0.25
        if best_score is None or s > best_score:
            best_score = s
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]