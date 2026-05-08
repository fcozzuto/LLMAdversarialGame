def choose_move(observation):
    w = int(observation["grid_width"] or 8)
    h = int(observation["grid_height"] or 8)
    sx, sy = observation["self_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    unclaimed = [(c[0], c[1]) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2]
    opp_t = [(c[0], c[1]) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2]
    opp_pos = observation["opponent_position"]
    ox, oy = opp_pos[0], opp_pos[1]

    if opp_t:
        # Prefer stealing squares adjacent to opponent territory; else approach its centroid.
        opp_set = set(opp_t)
        cand = []
        for x, y in unclaimed:
            if not free(x, y): 
                continue
            adj = any((x + dx, y + dy) in opp_set for dx, dy in neigh8)
            if adj:
                d = abs(x - sx) + abs(y - sy)
                score = (0, d, abs(x - ox) + abs(y - oy), x, y)
                cand.append((score, (x, y)))
        if not cand:
            cx = sum(x for x, y in opp_t) / len(opp_t)
            cy = sum(y for x, y in opp_t) / len(opp_t)
            cand = [((abs(cx - x) + abs(cy - y), abs(x - sx) + abs(y - sy), x, y), (x, y))
                    for x, y in unclaimed if free(x, y)]
        if cand:
            cand.sort(key=lambda t: t[0])
            tx, ty = cand[0][1]
        else:
            tx, ty = ox, oy
    else:
        tx, ty = ox, oy
        # If unclaimed exists, go to the nearest unclaimed.
        if unclaimed:
            best = None
            for x, y in unclaimed:
                if free(x, y):
                    d = abs(x - sx) + abs(y - sy)
                    if best is None or (d, x, y) < best[0]:
                        best = ((d, x, y), (x, y))
            if best:
                tx, ty = best[1]

    # Choose best 1-step move that reaches/approaches target while avoiding obstacles.
    best_move = [0, 0]
    best_key = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in [(0, 0)] + neigh8:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny) and (dx != 0 or dy != 0):
            continue
        # Prefer moves that enter opponent territory (flip) or unclaimed near it.
        opp_set2 = set(opp_t)
        enters_opp = (nx, ny) in opp_set2
        enters_un = (nx, ny) in set(unclaimed) if unclaimed else False
        dist = abs(nx - tx) + abs(ny - ty)
        # Tie-break deterministically: closer to target, then enter opponent, then enter unclaimed, then lexicographic move.
        key = (dist, 0 if enters_opp else 1, 0 if enters_un else 1, dx, dy)
        if key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move