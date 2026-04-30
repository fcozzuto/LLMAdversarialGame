def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # If no resources, move to increase distance from opponent deterministically.
    if not resources:
        best = None
        bestd = -1
        for dx, dy, nx, ny in candidates:
            d = md((nx, ny), (ox, oy))
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best else [0, 0]

    # Otherwise: prefer resources where we can arrive earlier than opponent, and penalize being late.
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in candidates:
        my_to_opp = md((nx, ny), (ox, oy))
        # Score lower is better.
        score = None
        for rx, ry in resources:
            myd = md((nx, ny), (rx, ry))
            opd = md((ox, oy), (rx, ry))
            late_pen = 0 if myd < opd else (2 + (myd - opd) * 0.5)
            # Also discourage moves that bring us closer to opponent when we are not winning the race.
            opp_risk = 0.15 * my_to_opp if myd >= opd else 0.0
            s = myd + late_pen + opp_risk
            if score is None or s < score:
                score = s
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]