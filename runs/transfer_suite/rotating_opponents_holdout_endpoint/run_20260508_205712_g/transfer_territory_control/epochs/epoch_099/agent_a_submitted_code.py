def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(x):
        s = set()
        if not x:
            return s
        for c in x:
            if c and len(c) >= 2:
                s.add((int(c[0]), int(c[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    self_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))

    lead = int(observation.get("self_territory_count") or 0) >= int(observation.get("opponent_territory_count") or 0)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)
    def touches_opp(x, y):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (x + dx, y + dy) in opp_t:
                return True
        return False

    if resources:
        targets = list(resources)
    elif unclaimed:
        targets = list(unclaimed)
    else:
        targets = [(ox, oy)]

    def nearest_dist(x, y, cells):
        best = 10**9
        for tx, ty in cells:
            d = man(x, y, tx, ty)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in resources:
            score += 100000 - nearest_dist(nx, ny, targets) * 3
        if (nx, ny) in unclaimed:
            score += 30000 if lead else 20000
            if not lead and touches_opp(nx, ny):
                score += 80000
        if (nx, ny) in opp_t:
            score += 60000 if not lead else -20000
        if lead and (nx