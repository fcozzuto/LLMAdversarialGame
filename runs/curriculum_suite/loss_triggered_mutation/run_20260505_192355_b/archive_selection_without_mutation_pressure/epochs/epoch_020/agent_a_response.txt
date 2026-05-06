def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose the move that (1) secures a resource where we are clearly closer,
    # else (2) "chokes" by moving to reduce opponent's progress to its best target.
    best = [0, 0]
    best_val = -10**18
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue

            secure_found = False
            secure_best_gap = -10**18
            secure_best_self = 10**18

            opp_best = None  # tuple (gap, opp_d, self_d) for best opponent-targeting
            for rx, ry in resources:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                gap = od - sd  # positive means we are closer than opponent
                if sd <= od - 1:
                    secure_found = True
                    # Prefer bigger advantage; tie-break by smaller self distance
                    if gap > secure_best_gap or (gap == secure_best_gap and sd < secure_best_self):
                        secure_best_gap, secure_best_self = gap, sd
                # Opponent choke: consider resources opponent can reach first (or tied)
                if opp_best is None:
                    opp_best = (-gap, od, sd)
                else:
                    # minimize opponent's od while also avoiding giving ourselves worse positioning
                    cand = (-gap, od, sd)
                    if cand < opp_best:
                        opp_best = cand

            if secure_found:
                # Strongly commit to guaranteed-leaning grabs
                val = 1000000 + secure_best_gap * 1000 - secure_best_self
            else:
                # No clear grab: reduce opponent's best target distance and increase our relative pressure
                if opp_best is None:
                    val = -sd if False else 0
                else:
                    # opp_best = (neg_gap, opp_d, self_d); smaller is better
                    neg_gap, od, sd = opp_best
                    val = -od * 5 + (od - sd) * 10 - sd
            if val > best_val:
                best_val = val
                best = [dx, dy]

    return best