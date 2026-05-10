def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    uset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    oset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    sset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    eset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Prefer expanding into unclaimed cells adjacent to our territory.
    if sset:
        adj_unclaimed = []
        for (x, y) in sset:
            for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in uset:
                    adj_unclaimed.append((nx, ny))
        targets = adj_unclaimed
    else:
        targets = []

    if not targets:
        targets = list(uset)
    if not targets:
        targets = [(ox, oy)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue

        # Heuristic value: claim unclaimed strongly, contest opponent, and move closer to best target.
        if (nx, ny) in uset:
            base = 40
        elif (nx, ny) in eset:
            base = 20
        else:
            base = 5

        # Encourage moving toward the nearest target; also avoid moving too deep into opponent territory unless it helps.
        nearest_t = 10**9
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            if d < nearest_t:
                nearest_t = d

        # Penalize proximity to opponent if already flipping is unlikely; reward nearing their territory to pressure edges.
        opp_dist = man(nx, ny, ox, oy)
        opp_bonus = 0
        if eset:
            # distance to nearest opponent cell
            nearest_opp = 10**9
            for ex, ey in eset:
                d = man(nx, ny, ex, ey)
                if d < nearest_opp:
                    nearest_opp = d
            opp_bonus = (8 - min(nearest_opp, 8)) * 2

        v = base + (30 - nearest_t) + opp_bonus - (opp_dist // 3)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]