def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    cx, cy = (w - 1) // 2, (h - 1) // 2

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if x is not None and y is not None:
                obstacles.add((int(x), int(y)))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = [(int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []) if x is not None and y is not None]
    if not unclaimed:
        return [0, 0]

    dirs8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    center = (cx, cy)
    opp_adj = []
    for x, y in unclaimed:
        ok = False
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp:
                ok = True
                break
        if ok:
            opp_adj.append((x, y))

    targets = opp_adj if opp_adj else unclaimed
    best_t = None
    best_key = None
    for x, y in targets:
        # Prefer cells near center but also reachable; deterministic lexicographic tie.
        d_center = abs(x - center[0]) + abs(y - center[1])
        d_self = abs(x - sx) + abs(y - sy)
        key = (d_center, d_self, x, y)
        if best_key is None or key < best_key:
            best_key, best_t = key, (x, y)

    tx, ty = best_t
    moves = [(0, 0)] + dirs8
    best_m = [0, 0]
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer moving toward target; then prefer flipping by stepping into opponent territory.
        dist = abs(nx - tx) + abs(ny - ty)
        into_opp = 1 if (nx, ny) in opp else 0
        # Also prefer moves adjacent to opponent territory to create counterclaim pressure.
        adj_opp = 0
        for adx, ady in dirs8:
            if (nx + adx, ny + ady) in opp:
                adj_opp = 1
                break
        key = (dist, -into_opp, -adj_opp, dx, dy)
        if best_mkey is None or key < best_mkey:
            best_mkey, best_m = key, [dx, dy]

    return [int(best_m[0]), int(best_m[1])]