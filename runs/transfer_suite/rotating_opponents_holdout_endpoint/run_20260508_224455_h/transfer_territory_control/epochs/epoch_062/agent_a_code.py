def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(obj):
        s = set()
        for c in obj or []:
            try:
                x, y = c
            except:
                continue
            try:
                s.add((int(x), int(y)))
            except:
                pass
        return s

    un = to_set(observation.get("unclaimed_cells"))
    myt = to_set(observation.get("self_territory"))
    opt = to_set(observation.get("opponent_territory"))
    obst = to_set(observation.get("obstacles"))
    res = to_set(observation.get("resources"))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    adj4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_to_opp(x, y):
        return abs(x - ox) + abs(y - oy)

    def unclaimed_adj(x, y):
        c = 0
        for dx, dy in adj4:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in un:
                c += 1
        return c

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        score = 0
        if (nx, ny) in res:
            score += 5
        score += 2 * unclaimed_adj(nx, ny)
        if (nx, ny) in opt:
            score -= 6
        if (nx, ny) in myt:
            score += 1
        score -= 0.5 * dist_to_opp(nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best