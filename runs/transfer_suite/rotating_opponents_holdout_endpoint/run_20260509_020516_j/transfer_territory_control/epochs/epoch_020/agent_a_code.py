def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
            else:
                x, y = int(p.get("x", 0)), int(p.get("y", 0))
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))
        except Exception:
            pass

    opp_tr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    opp_adj = set()
    dirs8 = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for (x, y) in opp_tr:
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs and (nx, ny) not in opp_tr:
                opp_adj.add((nx, ny))

    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in dirs8 + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obs:
            continue

        s = 0
        if (nx, ny) in opp_tr:
            s += 300  # immediate flip pressure
            s += max(0, 20 - (abs(nx - ox) + abs(ny - oy)))  # approach opponent
        elif (nx, ny) in unclaimed:
            s += 140
            if (nx, ny) in opp_adj:
                s += 160  # grab frontier for fast expansion
        else:
            # stepping into own territory/neutral-ish: small preference for moves that open frontier next
            s += 5

        # Prefer moves that increase closeness to opponent frontier/position
        d_opp = abs(nx - ox) + abs(ny - oy)
        s += 30 - d_opp

        # Minor penalty if moving away from any frontier-adjacent area
        if opp_adj:
            # deterministic nearest-distance approximation using two axes
            # (no heavy search; local estimate via min over a few sample points)
            sample = list(opp_adj)
            m = 10**9
            for i in range(0, min(len(sample), 9)):
                x, y = sample[i]
                dd = abs(nx - x) + abs(ny - y)
                if dd < m:
                    m = dd
            if m < 10**9:
                s += 15 - m

        if s > best_score:
            best_score = s
            best_move = [dx, dy]

    return best_move