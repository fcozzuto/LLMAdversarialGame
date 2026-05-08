def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (None, -10**18)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**18
        d_opp = abs(x - ox) + abs(y - oy)
        d_self = abs(x - sx) + abs(y - sy)
        # expansion: prefer unclaimed/resources, also prefer pushing away from opponent
        v = 0
        if (x, y) in resources:
            v += 60
        if (x, y) in unclaimed:
            v += 20
        if (x, y) in oppT:
            # entering opponent territory flips; reward it but still prefer positions that increase separation
            v += 35
        if (x, y) in selfT:
            v += 6
        # stay safe: avoid stepping into squares adjacent to obstacles too often
        adj_obs = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    adj_obs += 1
        v += 3 * d_opp - 2 * d_self - 10 * adj_obs
        return v

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = cell_value(nx, ny)
        # deterministic tie-break: higher v, then prefer non-stay, then lexicographic move
        if v > best[1] or (v == best[1] and (best[0] is None or (dx, dy) < best[0])):
            best = ((dx, dy), v)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]