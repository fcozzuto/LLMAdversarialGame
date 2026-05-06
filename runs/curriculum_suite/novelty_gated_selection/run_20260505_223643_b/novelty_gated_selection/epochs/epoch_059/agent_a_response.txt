def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (0, 1), (-1, 1), (1, 1)]

    def md2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_mv = (0, 0)

    # Deterministic preference tuning
    alpha = 0.9  # reward being closer than opponent
    beta = 0.08  # keep moving toward something
    edge_bonus = 0.02

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_best = 10**18
        opp_best = 10**18
        for rx, ry in resources:
            myd = md2(nx, ny, rx, ry)
            opd = md2(ox, oy, rx, ry)
            if myd < my_best:
                my_best = myd
            if opd < opp_best:
                opp_best = opd

        # More granular: consider best contest on any single resource
        contest = -10**18
        for rx, ry in resources:
            myd = md2(nx, ny, rx, ry)
            opd = md2(ox, oy, rx, ry)
            # positive if we are closer than opponent for that resource
            gap = opd - myd
            if gap > contest:
                contest = gap

        score = alpha * contest - beta * my_best
        # slight bias toward edges/corners to reduce opponent overlap (safe collector often funnels)
        if nx in (0, w - 1) or ny in (0, h - 1):
            score += edge_bonus

        if best is None or score > best:
            best = score
            best_mv = (dx, dy)
        elif score == best:
            # deterministic tie-break: prefer smaller move magnitude, then lexicographic
            m1 = abs(best_mv[0]) + abs(best_mv[1])
            m2 = abs(dx) + abs(dy)
            if m2 < m1 or (m2 == m1 and (dx, dy) < best_mv):
                best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]