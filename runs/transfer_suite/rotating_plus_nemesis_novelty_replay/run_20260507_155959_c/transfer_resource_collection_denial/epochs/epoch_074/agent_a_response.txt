def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) != (sx, sy) and (nx, ny) not in obs:
                valid.append((dx, dy))
    valid.append((0, 0))
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    opp_dist = lambda x, y: abs(x - ox) + abs(y - oy)
    self_dist = lambda x, y: abs(x - x0) + abs(y - y0)

    best_score = None
    best_move = (0, 0)
    for dx, dy in valid:
        x0, y0 = sx + dx, sy + dy
        step_score = 0
        if (x0, y0) in res:
            step_score += 10000
        # Evaluate as: pick the resource that gives maximum "capture advantage"
        # advantage = (opp_dist - self_dist), prefer being closer and also reduce own distance.
        local_best = -10**9
        for rx, ry in res:
            sd = abs(rx - x0) + abs(ry - y0)
            od = abs(rx - ox) + abs(ry - oy)
            adv = od - sd
            # Encourage quick collection even if not strictly first
            val = adv * 50 - sd
            if val > local_best:
                local_best = val
        step_score += local_best
        # Secondary: avoid moving toward being trapped by opponent (minor bias)
        step_score += -((abs(x0 - ox) + abs(y0 - oy)) // 8)
        if best_score is None or step_score > best_score or (step_score == best_score and (dx, dy) < best_move):
            best_score = step_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]