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
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = resources

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    # Find a nearby unclaimed target; if none, bias toward center.
    if unclaimed:
        nearest = None
        bestd = 10**9
        for (x, y) in unclaimed:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
                nearest = (x, y)
        tx, ty = nearest
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Heuristic scoring
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_self = (nx, ny) in selfT
        is_opp = (nx, ny) in oppT
        is_uncl = (nx, ny) in unclaimed

        # immediate cell desirability
        cell = 0
        if is_uncl:
            cell += 4
        if is_self:
            cell += 1
        if is_opp:
            cell -= 3  # entering opponent territory is risky vs sweeper

        # greedy progress toward target
        curd = abs(tx - sx) + abs(ty - sy)
        nd = abs(tx - nx) + abs(ty - ny)
        prog = 2 * (curd - nd)

        # avoid getting too close to opponent unless it also improves progress/claims
        oppd = abs(ox - sx) + abs(oy - sy)
        noppd = abs(ox - nx) + abs(oy - ny)
        sep = noppd - oppd  # positive good
        risk = 0
        if is_opp:
            risk += 3  # add risk for flipping entry
        if noppd <= 1:
            risk += 6

        # small tie-break to prefer deterministic, non-oscillatory bias: move that keeps x then y minimal
        tie = -(dx * 3 + dy)

        score = cell + prog + sep - risk + tie
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]