def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def mdist(a, b, x, y):
        return abs(x - a) + abs(y - b)

    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move, best_score = [0, 0], None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = abs(nx - cx) + abs(ny - cy)
            key = (-d, abs(nx - ox) + abs(ny - oy))
            if best_score is None or key > best_score:
                best_score, best_move = key, [dx, dy]
        return best_move

    # Contest resources: prioritize moves that are strictly closer than opponent to some resource.
    # If many are contested, also prefer those that are close to me.
    best_move, best_key = [0, 0], None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        my_best = 10**9
        opp_worst = -10**9
        contest_bonus = 0
        near_bonus = 0
        for rx, ry in res:
            d_my = mdist(nx, ny, rx, ry)
            d_opp = mdist(ox, oy, rx, ry)
            if d_my < my_best:
                my_best = d_my
            if d_opp - d_my > 0:
                contest_bonus += 1
                if d_my <= 2:
                    near_bonus += 2
                if d_opp - d_my >= 3:
                    near_bonus += 1
            if d_opp < opp_worst:
                opp_worst = d_opp
        # Key: maximize contest/near and minimize my_best; also slightly prefer distancing from opponent.
        key = (contest_bonus, near_bonus, -my_best, mdist(nx, ny, ox, oy))
        if best_key is None or key > best_key:
            best_key, best_move = key, [dx, dy]
    return best_move