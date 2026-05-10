def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    sr = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in sr) or ("pursue" in sr)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    pref = [(0,0),(1,1),(-1,-1),(1,-1),(-1,1),(1,0),(-1,0),(0,1),(0,-1)]
    order = [m for m in pref if m in moves] + [m for m in moves if m not in pref]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    def free_neighbors(x, y):
        c = 0
        for a, b in moves:
            nx, ny = x + a, y + b
            if ok(nx, ny):
                c += 1
        return c

    best = None
    best_score = None
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d1 = dist(nx, ny)
        # 1-step lookahead: assume opponent moves greedily opposite objective
        best_opp_d = None
        for ad, bd in moves:
            ax, ay = nx + ad, ny + bd
            if not ok(ax, ay):
                continue
            d2 = abs(ax - ox) + abs(ay - ox)  # dummy to keep deterministic? (avoid); use proper:
        # proper: opponent position is fixed for our turn; only our lookahead matters:
        # score uses our projected next distance only (simple and deterministic).

        fn = free_neighbors(nx, ny)
        # Heuristic weights: capture radius is 0; avoid collisions with obstacles via ok().
        # pursuer: minimize distance; evader: maximize distance. Tie-break by mobility and staying near diagonal.
        if is_pursuer:
            score = (-d1 * 1000) + (fn * 3)
        else:
            score = (d1 * 1000) + (fn * 3)

        # Diagonal alignment bonus to counter zigzag evasion patterns
        ax = nx - ox
        ay = ny - oy
        diag_bonus = -abs(abs(ax) - abs(ay)) if is_pursuer else abs(abs(ax) - abs(ay))
        score += diag_bonus

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]