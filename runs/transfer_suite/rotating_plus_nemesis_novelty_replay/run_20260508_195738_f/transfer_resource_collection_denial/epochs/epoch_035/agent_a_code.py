def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = (0, 0)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestc = None
        for cx, cy in corners:
            key = (-manh(ox, oy, cx, cy), manh(sx, sy, cx, cy))
            if bestc is None or key < bestc[0]:
                bestc = (key, (cx, cy))
        tx, ty = bestc[1]
        bestm = (None, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            key = (manh(nx, ny, tx, ty), manh(nx, ny, ox, oy))
            if bestm[0] is None or key < bestm[0]:
                bestm = (key, (dx, dy))
        return bestm[1] if bestm[1] is not None else [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        reach_gap = do - ds  # positive means we can reach earlier
        # Prefer immediate wins, then deny, then nearest.
        key = (
            -reach_gap,                 # smaller is better -> higher reach_gap
            ds,                          # prefer closer
            -min(do, 99),               # if tie, pick one where opponent is far
            rx, ry
        )
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    bestm = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = manh(nx, ny, tx, ty)
        # Extra: if move steps toward any resource that we could beat sooner than opponent, boost it.
        bonus = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            ds2 = manh(nx, ny, rx, ry)
            do2 = manh(ox, oy, rx, ry)
            gap = do2 - ds2
            if gap > 0:
                bonus = max(bonus, gap)
        # Prefer reducing distance to target, and (slightly) increasing our advantage.
        key = (d, -(bonus), manh(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            bestm = (dx, dy)

    return list(bestm) if bestm is not None else [0, 0]