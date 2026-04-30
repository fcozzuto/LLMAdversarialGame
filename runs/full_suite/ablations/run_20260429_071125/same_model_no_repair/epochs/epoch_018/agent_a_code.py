def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def safety_at(x, y):
        if (x, y) in occ:
            return 10**9
        s = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            if (x+dx, y+dy) in occ:
                s += 30
        for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            if (x+dx, y+dy) in occ:
                s += 14
        return s

    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_val = -10**18
    best = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        s_here = safety_at(nx, ny)
        if s_here >= 10**8:
            continue

        # Evaluate best resource for this move: prefer improving our advantage vs opponent.
        cur_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            myd = manh(nx, ny, rx, ry)
            opd = manh(ox, oy, rx, ry)
            # Advantage: lower myd than opd is good; being equal/behind is bad.
            adv = opd - myd
            # Add small tie-breakers: slightly prefer closer overall and safer target region.
            near_opp = manh(rx, ry, ox, oy)
            opp_block = 0
            if near_opp <= 1:
                opp_block = 55
            elif near_opp <= 2:
                opp_block = 20
            tgt_safety = safety_at(rx, ry)
            val = 20 * adv - myd - opp_block - (tgt_safety // 10) - s_here
            if val > cur_best:
                cur_best = val
        # If we can't improve toward any resource, still prefer reducing safety and getting closer to some.
        if cur_best > best_val:
            best_val = cur_best
            best = (dx, dy)

    # Deterministic fallback if all moves invalid (should be rare)
    if best_val == -10**18:
        for dx, dy in [(0,0), (1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,1), (1,-1), (-1,-1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in occ:
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]