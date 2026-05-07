def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if (sx, sy) in obstacles:
        return [0, 0]
    for rx, ry in resources:
        if (sx, sy) == (rx, ry):
            return [0, 0]
    if not resources:
        tx, ty = ((0, h - 1) if (sx + (h - 1 - sy)) >= ((w - 1 - sx) + sy) else (w - 1, 0))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obst_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    opp_best = None
    for rx, ry in resources:
        d = dist((ox, oy), (rx, ry))
        if opp_best is None or d < opp_best:
            opp_best = d

    best_score = None
    best_move = [0, 0]
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer moves that improve our lead toward resources vs opponent
        min_gap = None
        min_our = None
        for rx, ry in resources:
            our_d = dist((nx, ny), (rx, ry))
            opp_d = dist((ox, oy), (rx, ry))
            gap = opp_d - our_d  # positive means we're closer
            if min_gap is None or gap > min_gap:
                min_gap = gap
            if min_our is None or our_d < min_our:
                min_our = our_d
        # If we land on a resource, huge boost
        on_res = any((nx, ny) == (rx, ry) for rx, ry in resources)
        score = (min_gap * 2000) - (min_our * 10) - (obst_pen(nx, ny) * 50)
        if on_res:
            score += 10**7
        if opp_best is not None:
            score += (opp_best * 1)  # small deterministic bias across steps
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move