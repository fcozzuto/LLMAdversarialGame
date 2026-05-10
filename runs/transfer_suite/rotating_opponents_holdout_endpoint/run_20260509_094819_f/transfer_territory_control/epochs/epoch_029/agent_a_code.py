def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def to_set(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))

    if (sx, sy) in obstacles:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh8 = moves

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_kind(x, y):
        if (x, y) in obstacles:
            return -10
        if (x, y) in selfT:
            return 0
        if (x, y) in oppT:
            return 2
        if (x, y) in unclaimed:
            return 1
        return 0

    best = -10**9
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        k = cell_kind(nx, ny)
        if k < -5:
            score = -10**8
        else:
            score = 0
            # immediate gain
            score += 8 * k
            # expansion potential: adjacent unclaimed
            adj_un = 0
            adj_ours = 0
            for ddx, ddy in neigh8:
                ax, ay = nx + ddx, ny + ddy
                if not inb(ax, ay):
                    continue
                if (ax, ay) in unclaimed:
                    adj_un += 1
                if (ax, ay) in selfT:
                    adj_ours += 1
            score += 3 * adj_un + 1 * adj_ours
            # pressure/chase: prefer reducing distance to opponent
            d0 = abs(sx - ox) + abs(sy - oy)
            d1 = abs(nx - ox) + abs(ny - oy)
            score += 2 * (d0 - d1)
            # avoid giving opponent edge access: prefer staying away from their core if not taking it
            if k <= 0:
                score -= 0.5 * min((abs(nx - px) + abs(ny - py) for (px, py) in oppT), default=8)
            # tie-break: deterministic ordering based on move
            score += 0.0001 * (dx * 10 + dy)
        if score > best:
            best = score
            best_move = (nx - sx, ny - sy)

    bx, by = best_move
    if bx not in (-1, 0, 1) or by not in (-1, 0, 1):
        return [0, 0]
    return [int(bx), int(by)]