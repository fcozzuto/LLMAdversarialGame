def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestv = None
        for cx, cy in corners:
            v = (abs(cx - ox) - abs(sx - ox) + abs(cy - oy) - abs(sy - oy), -(abs(cx - sx) + abs(cy - sy)))
            if bestv is None or v > bestv:
                bestv = v
                best = (cx, cy)
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles:
            return [dx, dy]
        return [0, 0]

    # Evaluate moves by how well they win the race to a resource.
    best_move = (0, 0)
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Prefer moves that immediately get a resource.
        if (nx, ny) in res_set:
            score = (10**6, -0, -(abs(nx - ox) + abs(ny - oy)))
            best_move, best_score = (dx, dy), score
            break
        move_best = None
        for rx, ry in resources:
            sd = max(abs(rx - nx) + abs(ry - ny), 0)
            od = abs(rx - ox) + abs(ry - oy)
            # Lower ours is better; win if ours <= opponent
            win_margin = od - sd  # positive means we reach first
            tie_bonus = 1 if sd <= od else 0
            # Small penalty for moving away from that resource (steers directly)
            direct_pen = sd
            cand = (win_margin, tie_bonus, -direct_pen)
            if move_best is None or cand > move_best:
                move_best = cand
        score = (move_best[0], move_best[1], move_best[2], -((dx != 0) + (dy != 0)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]