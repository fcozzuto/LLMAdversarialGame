def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c is not None and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c is not None and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c is not None and len(c) >= 2)

    dirs = [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
    best = None
    best_val = None

    # Targets: prefer immediate counterclaim, else push into unclaimed near opponent.
    targets_opp = list(opp_t) if opp_t else []
    targets_unc = list(unclaimed) if unclaimed else []

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):  # invalid move => engine keeps place; avoid by treating as worst
            continue

        val = 0
        cell = (nx, ny)

        if cell in opp_t:
            val += 120  # direct flip priority
        elif cell in unclaimed:
            val += 55   # expand quickly
        elif cell in self_t:
            val += 5    # avoid wandering

        # Encourage moving toward nearest opponent territory first, else unclaimed.
        if targets_opp:
            dmin = 10**9
            for tx, ty in targets_opp:
                dd = abs(tx - nx) + abs(ty - ny)
                if dd < dmin:
                    dmin = dd
            val += (20 - dmin) * 3
        elif targets_unc:
            dmin = 10**9
            for tx, ty in targets_unc:
                dd = abs(tx - nx) + abs(ty - ny)
                if dd < dmin:
                    dmin = dd
            val += (18 - dmin) * 2

        # Slightly prefer not to get stuck near own corner late.
        dist_to_center = abs(nx - (w//2)) + abs(ny - (h//2))
        val -= dist_to_center * 0.1

        # Deterministic tie-break: stable order from dirs (handled by first best)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]