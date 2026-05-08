def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    opp = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(opp[0]), int(opp[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    un = to_set("unclaimed_cells")

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    order = {d: i for i, d in enumerate(dirs)}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Targets: prefer nearest unclaimed, then nearest opponent territory; fallback to opponent
    if un:
        t1 = min(un, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        t1 = None
    if opp_t:
        t2 = min(opp_t, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        t2 = None

    target = t1 if t1 is not None else (t2 if t2 is not None else (ox, oy))

    def score_cell(nx, ny, dx, dy):
        # Base: move toward target
        base = -(abs(nx - target[0]) + abs(ny - target[1]))
        # Territory interactions
        if (nx, ny) in opp_t:
            base += 60  # flipping opponent territory on entry is strong
        elif (nx, ny) in un:
            base += 25  # expand into unclaimed
        elif (nx, ny) in self_t:
            base += 5   # consolidation
        # Avoid moving away from opponent too much
        base += -0.5 * (abs(nx - ox) + abs(ny - oy))
        # Slight preference for continuing direction (reduces dithering)
        if dx != 0 and dy != 0:
            base += 1
        return base

    # Choose best legal step; obstacles effectively make move invalid -> keep in place
    best = (None, -10**18)
    for dx, dy in sorted(dirs, key=lambda d: order[d]):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        val = score_cell(nx, ny, dx, dy)
        if val > best[1]:
            best = ((dx, dy), val)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]