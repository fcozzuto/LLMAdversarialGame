def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors(nx, ny):
        res = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                x, y = nx + dx, ny + dy
                if inb(x, y) and (x, y) not in obstacles:
                    res.append((dx, dy))
        return res

    targets = observation.get("unclaimed_cells", None)
    if targets is None:
        targets = observation.get("resources", None)
    if not targets:
        targets = [(w // 2, h // 2)]
    targets = [tuple(p) for p in targets if isinstance(p, (list, tuple)) and len(p) == 2 and inb(p[0], p[1]) and tuple(p) not in obstacles]
    if not targets:
        targets = [(w // 2, h // 2)]

    opps = []
    for t in (observation.get("opponent_territory", []) or []):
        p = tuple(t)
        if len(p) == 2 and inb(p[0], p[1]) and p not in obstacles:
            opps.append(p)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cand = [(0, 0)]
    cand += neighbors(sx, sy)

    best = None
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        d_to_opp = man(nx, ny, ox, oy)
        t_best = None
        t_dist = None
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            if t_dist is None or d < t_dist:
                t_dist = d
                t_best = (tx, ty)
        opp_terr_pen = 0
        if opps:
            d_opterr = min(man(nx, ny, ex, ey) for ex, ey in opps)
            opp_terr_pen = 2 if d_opterr == 0 else 0
        score = (d_to_opp * 3) - (t_dist if t_dist is not None else 0) - opp_terr_pen
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]