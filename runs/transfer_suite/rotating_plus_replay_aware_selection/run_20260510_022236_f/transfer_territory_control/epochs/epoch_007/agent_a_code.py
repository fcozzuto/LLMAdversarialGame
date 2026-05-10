def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))
    unclaimed = to_set(observation.get("unclaimed_cells", observation.get("unclaimed")))
    opp_terr = to_set(observation.get("opponent_territory"))
    self_terr = to_set(observation.get("self_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**12
        sc = 0
        if (x, y) in resources:
            sc += 120
        if (x, y) in unclaimed:
            sc += 70
        if (x, y) in opp_terr:
            sc += 55
        if (x, y) in self_terr:
            sc += 10
        dc = abs(x - (w - 1) / 2.0) + abs(y - (h - 1) / 2.0)
        sc -= int(dc)
        dops = abs(x - ox) + abs(y - oy)
        sc -= 2 * dops
        return sc

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score(nx, ny)
        if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]