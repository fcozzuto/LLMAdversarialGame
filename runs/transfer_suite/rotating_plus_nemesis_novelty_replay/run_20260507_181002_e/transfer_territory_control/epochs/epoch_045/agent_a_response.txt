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
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    if not unclaimed:
        return [0, 0]

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield (nx, ny)

    # Prefer cells that contest the opponent territory (adjacent to opp)
    opp_adj = set()
    for (x, y) in oppT:
        if (x, y) not in obstacles:
            for c in neigh8(x, y):
                if c in unclaimed and c not in obstacles:
                    opp_adj.add(c)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    candidates = opp_adj if opp_adj else unclaimed
    best = None
    bestv = -10**18

    for tx, ty in candidates:
        if (tx, ty) in obstacles:
            continue
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        dc = abs(tx - cx) + abs(ty - cy)
        # Make counter-claim attractive: closer to opponent boundary, not too far from center
        v = (-1.2 * ds) + (0.9 * (do)) - (0.05 * dc)
        if opp_adj:
            # hard boost for adjacent-to-opp flips
            v += 50 - 3 * ds
        else:
            v += 5 - 0.1 * dc
        if v > bestv:
            bestv = v
            best = (tx, ty)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestmv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # prefer stepping toward the chosen target; also prefer stepping into unclaimed
        step_to = man(nx, ny, tx, ty)
        into = 1 if (nx, ny) in unclaimed else 0
        into_opp = 1 if (nx, ny) in oppT else 0
        v = (-2.0 * step_to) + 3.0 * into + 1.5 * into_opp
        if v > bestmv:
            bestmv = v
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]