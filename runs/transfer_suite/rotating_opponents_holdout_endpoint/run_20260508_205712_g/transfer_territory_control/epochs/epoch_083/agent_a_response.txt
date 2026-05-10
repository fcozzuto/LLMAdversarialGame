def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_tr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_tr.add((x, y))

    opp_tr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_tr.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    res = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in opp_tr:
            score += 120
        elif (nx, ny) in unclaimed:
            score += 35
        elif (nx, ny) in self_tr:
            score += 5
        else:
            score += 8

        if (nx, ny) in res:
            score += 25

        # Frontier pressure: prefer moves that are adjacent to unclaimed and/or opponent territory
        adj_un = 0
        adj_opp = 0
        adj_self = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                if (ax, ay) in unclaimed:
                    adj_un += 1
                if (ax, ay) in opp_tr:
                    adj_opp += 1
                if (ax, ay) in self_tr:
                    adj_self += 1
        score += 6 * adj_un + 10 * adj_opp - 1 * adj_self

        # Mild bias toward the nearest opponent territory cell to counterclaim deterministically
        if opp_tr:
            dmin = min((abs(nx - ox) + abs(ny - oy) for (ox, oy) in opp_tr))
            score += max(0, 20 - dmin)

        # Deterministic tie-breaker: lexicographically smallest move among equals
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]