def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obst = set()
    for c in observation.get("obstacles") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obst.add((int(c[0]), int(c[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def mindist_to_set(x, y, S):
        if not S:
            return 999
        return min(abs(x - a) + abs(y - b) for (a, b) in S)

    opp_dist = mindist_to_set(sx, sy, oppT)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    bestv = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            nx, ny = sx, sy
            dx, dy = 0, 0
        v = 0

        if (nx, ny) in unclaimed:
            v += 4
        if (nx, ny) in selfT:
            v += 1
        if (nx, ny) in oppT:
            v += 8  # prefer flipping opponent territory

        # Frontier/pressure: move closer to opponent territory
        nd = mindist_to_set(nx, ny, oppT)
        if oppT:
            v += 3 * (opp_dist - nd)

        # Center control slight preference
        v -= 0.05 * (abs(nx - cx) + abs(ny - cy))

        # Avoid aimless wandering: prefer increasing neighbors count of free cells
        free_n = 0
        for ex, ey in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            tx, ty = nx + ex, ny + ey
            if inside(tx, ty) and (tx, ty) not in obst:
                free_n += 1
        v += 0.02 * free_n

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]