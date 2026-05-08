def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (sx, sy))
    ox, oy = int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def to_set(v):
        s = set()
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    s.add((int(p[0]), int(p[1])))
        return s

    self_set = to_set(observation.get("self_territory"))
    opp_set = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    nbrs8 = dirs

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def is_adj_to(s, x, y):
        for dx, dy in nbrs8:
            if (x + dx, y + dy) in s:
                return True
        return False

    best = (None, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 100
        if (nx, ny) in self_set:
            score += 10
        if (nx, ny) in opp_set:
            score -= 120
        if is_adj_to(unclaimed, nx, ny):
            score += 20
        if is_adj_to(opp_set, nx, ny):
            score -= 35
        d0 = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)
        d1 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score += (d1 - d0) * 0.05
        if score > best[1]:
            best = ([dx, dy], score)

    return best[0] if best[0] is not None else [0, 0]