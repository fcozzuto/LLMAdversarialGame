def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    rs = [(r[0], r[1]) for r in resources]
    if not rs:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = (abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy), dx, dy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    on_resource = (sx, sy) in set(rs)
    if on_resource:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    opp_target = min(rs, key=lambda p: man(ox, oy, p[0], p[1]))
    opp_dist_map = {p: man(ox, oy, p[0], p[1]) for p in rs}

    best_move = (0, 0)
    bestv = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        self_best_dist = min(man(nx, ny, p[0], p[1]) for p in rs)
        # Evaluate by best "winning" target after this move
        wins = []
        for p in rs:
            d_self = man(nx, ny, p[0], p[1])
            d_opp = opp_dist_map[p]
            if d_self <= d_opp:
                wins.append((d_self, -d_opp, p[0], p[1]))
        if wins:
            wins.sort()
            v = (0, wins[0][0], wins[0][1], wins[0][2], wins[0][3], dx, dy)
        else:
            # Otherwise drift toward reducing gap to the closest resource
            closest = min(rs, key=lambda p: man(nx, ny, p[0], p[1]))
            v = (1, self_best_dist, man(nx, ny, closest[0], closest[1]), -man(ox, oy, closest[0], closest[1]), dx, dy)
        if bestv is None or v < bestv:
            bestv = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]