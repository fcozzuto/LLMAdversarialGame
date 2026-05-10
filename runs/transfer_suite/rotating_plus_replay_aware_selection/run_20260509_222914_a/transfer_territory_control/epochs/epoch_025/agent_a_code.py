def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    sxdir = 0 if ox == sx else (1 if ox > sx else -1)
    sydir = 0 if oy == sy else (1 if oy > sy else -1)

    def adj_self_count(x, y):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in self_terr:
                c += 1
        return c

    def min_dist_to_set(p, S):
        if not S:
            return 99
        px, py = p
        best = 99
        for qx, qy in S:
            d = abs(px - qx) + abs(py - qy)
            if d < best:
                best = d
        return best

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        in_opp = (nx, ny) in opp_terr
        in_own = (nx, ny) in self_terr
        in_un = (nx, ny) in unclaimed

        score = 0.0
        if in_opp:
            score += 6.5
        elif in_un:
            score += 2.25
        elif in_own:
            score += 0.1

        score += 0.9 * adj_self_count(nx, ny)

        # Keep pressure while reducing risk near opponent mass
        d_to_opp = min_dist_to_set((nx, ny), opp_terr)
        score += (0.35 if d_to_opp >= 3 else -0.15 * d_to_opp)

        # Deterministic directional bias toward opponent
        score += 0.25 * ((nx - sx) * sxdir + (ny - sy) * sydir)

        # Tie-break deterministically: prefer moves with larger dx, then dy, then lower abs(dx)+abs(dy)
        key = (score, -abs(dx) - abs(dy), dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]