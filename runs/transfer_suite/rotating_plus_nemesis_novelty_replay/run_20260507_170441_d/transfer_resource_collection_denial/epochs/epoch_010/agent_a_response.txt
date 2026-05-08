def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick resource where we are relatively closer than opponent (ties by nearest resource index deterministically)
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        key = (opd - myd, -myd, -rx, -ry)  # maximize gain, then closer, deterministic
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # Candidate moves
    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    res_set = set((p[0], p[1]) for p in resources)

    # Score moves: move toward target, avoid obstacles, and slightly prefer moves that deny opponent proximity
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        # Obstacle proximity penalty (avoid walking near obstacles)
        prox_pen = 0
        if obstacles:
            m = 10**18
            for px, py in obstacles:
                m = min(m, d2(nx, ny, px, py))
            if m <= 1:
                prox_pen -= 50
            elif m <= 4:
                prox_pen -= 12

        # Target progress
        cur = d2(sx, sy, tx, ty)
        nxt = d2(nx, ny, tx, ty)
        prog = (cur - nxt)

        # Resource collection bonus
        collect = 0
        if (nx, ny) in res_set:
            collect += 1000

        # Opponent denial: increase score if opponent would be farther from this cell than we are
        my_next = d2(nx, ny, tx, ty)
        opp_next = d2(ox, oy, tx, ty)
        deny = 0
        if my_next <= opp_next:
            deny += 8
        else:
            deny -= 3

        total = prog + collect + prox_pen + deny

        # Tie-break deterministically: prefer smaller |dx|+|dy| then lexicographic
        tie = (-abs(dx) - abs(dy), dx, dy)
        score_tuple = (total, tie)
        if score_tuple > (best_score, (-abs(best_move[0]) - abs(best_move[1]), best_move[0], best_move[1])):
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]