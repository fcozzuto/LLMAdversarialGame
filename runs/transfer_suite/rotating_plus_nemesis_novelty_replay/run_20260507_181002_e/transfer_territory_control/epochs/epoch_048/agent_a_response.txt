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
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not unclaimed and not oppT:
        return [0, 0]

    # Precompute a few "frontier" targets: unclaimed adjacent to opponent territory
    frontier = []
    if unclaimed and oppT:
        for (x, y) in unclaimed:
            if (x + 1, y) in oppT or (x - 1, y) in oppT or (x, y + 1) in oppT or (x, y - 1) in oppT or (x + 1, y + 1) in oppT or (x - 1, y - 1) in oppT:
                frontier.append((x, y))
                if len(frontier) >= 10:
                    break

    target_list = frontier if frontier else list(unclaimed)[:20] if unclaimed else list(oppT)[:10]
    best = -10**18
    best_move = [0, 0]

    def score_cell(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**15
        if (x, y) in oppT:
            return 90  # strong counterclaim/flip
        if (x, y) in unclaimed:
            # claim only if we can get there sooner than opponent (approx)
            d1 = abs(x - sx) + abs(y - sy)
            d2 = abs(x - ox) + abs(y - oy)
            return 35 + (d2 - d1) * 2
        if (x, y) in selfT:
            return 8
        # moving into empty but not unclaimed shouldn't help; keep low
        return -2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        # additional shaping: move toward best local target
        if target_list:
            # prefer lowering distance to nearest target, especially frontier
            d_self = 10**9
            d_opp = 10**9
            for tx, ty in target_list:
                ds = abs(tx - nx) + abs(ty - ny)
                do = abs(tx - ox) + abs(ty - oy)
                if ds < d_self:
                    d_self = ds
                if do < d_opp:
                    d_opp = do
            sc += (d_opp - d_self) * 3 - d_self * 0.5
        # avoid obstacles indirectly by discouraging staying if move is valid
        if (nx, ny) != (sx, sy) and (nx, ny) in obstacles:
            sc = -10**15
        if sc > best:
            best = sc
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]