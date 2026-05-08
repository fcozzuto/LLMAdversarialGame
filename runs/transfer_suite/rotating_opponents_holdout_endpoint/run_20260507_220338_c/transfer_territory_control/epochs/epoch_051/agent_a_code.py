def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    def to_set(lst):
        s = set()
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    # Precompute a small sample of unclaimed for speed/determinism
    uc_list = list(unclaimed)
    uc_list.sort(key=lambda p: (p[0], p[1]))
    uc_sample = uc_list[:12]

    best = None
    bestv = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in unclaimed:
            base += 8
        elif (nx, ny) in oppT:
            base -= 6
        else:
            base += 1 if (nx, ny) in selfT else 0

        # Encourage moving toward frontier (nearest unclaimed)
        if uc_sample:
            dmin = 10**9
            for x, y in uc_sample:
                dd = abs(x - nx) + abs(y - ny)
                if dd < dmin: dmin = dd
            frontier = -dmin
        else:
            frontier = 0

        # Avoid opponent when possible (territory_counterclaim)
        dist_opp = abs(ox - nx) + abs(oy - ny)
        avoid = dist_opp * 0.08

        # Prefer not to get adjacent to opponent territory too often
        adj_opp = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in oppT:
                    adj_opp += 1
        anti_adj = -adj_opp * 0.6

        v = base + frontier + avoid + anti_adj
        key = (v, -man(nx, ny, ox, oy), nx, ny)  # deterministic tie-break
        if bestv is None or key > bestv:
            bestv = key
            best = [dx, dy]

    return best if best is not None else [0, 0]