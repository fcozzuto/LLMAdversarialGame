def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cell_from_r(r):
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return (pos[0], pos[1])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return None

    targets = []
    for r in resources:
        c = cell_from_r(r)
        if c is not None:
            targets.append(c)
    if not targets:
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Simple reachable evaluation: maximize advantage (opp nearest - self nearest),
    # plus a deny term that penalizes if opponent is significantly closer after move.
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        self_min = 10**9
        opp_min = 10**9
        self_m = None
        opp_m = None
        for tx, ty in targets:
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            if ds < self_min:
                self_min = ds
                self_m = (tx, ty)
            if do < opp_min:
                opp_min = do
                opp_m = (tx, ty)

        # Deny focus: prefer making us closer to the resource the opponent could reach soonest.
        deny_term = 0
        if opp_m is not None:
            deny_term = man(nx, ny, opp_m[0], opp_m[1]) - opp_min

        # Obstacle-adjacency penalty for safer paths (deterministic tie-break).
        adj_pen = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                ax, ay = nx + adx, ny + ady
                if (ax, ay) in blocked:
                    adj_pen += 1

        # Primary objective: advantage grows when opponent is farther from their nearest target than us.
        val = (opp_min - self_min) * 1000 - self_min * 2 + (-deny_term) * 10 - adj_pen
        # Deterministic tie-break: closer to self's best target, then lexicographic dx,dy.
        if best is None or val > best_val or (val == best_val and (self_min, dx, dy) < (best[0], best[1], best[2])):
            best_val = val
            best = (self_min, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]