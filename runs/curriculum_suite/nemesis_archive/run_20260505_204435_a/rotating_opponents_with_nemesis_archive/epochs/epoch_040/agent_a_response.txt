def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked

    def parse_pos(r):
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return (pos[0], pos[1])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return None

    targets = []
    for r in resources:
        p = parse_pos(r)
        if p is not None and legal(p[0], p[1]):
            targets.append((p[0], p[1]))

    if not targets:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if legal(nx, ny):
                    return [dx, dy]
        return [0, 0]

    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            if legal(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def d(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    best = None
    best_score = None

    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not legal(nsx, nsy):
            continue

        self_best = 10**9
        opp_best = 10**9
        gap_best = -10**9

        for tx, ty in targets:
            ds = d(nsx, nsy, tx, ty)
            do = d(ox, oy, tx, ty)
            if ds < self_best: self_best = ds
            if do < opp_best: opp_best = do
            gap = do - ds  # larger means we are closer than opponent
            if gap > gap_best: gap_best = gap

        # Prefer moves that:
        # 1) improve who can secure a resource (maximize gap_best)
        # 2) reduce our best distance
        # 3) avoid getting too close to opponent's current best target (small penalty)
        score = (gap_best, -self_best, self_best - opp_best)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]