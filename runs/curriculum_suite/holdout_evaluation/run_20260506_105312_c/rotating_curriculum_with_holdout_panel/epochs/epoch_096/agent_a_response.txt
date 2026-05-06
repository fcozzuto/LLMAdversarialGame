def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not inb(sx, sy) or (sx, sy) in obs:
        sx, sy = 0, 0

    if not resources:
        # drift to increase separation while staying valid
        best = (-(10**9), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                d = abs(nx - ox) + abs(ny - oy)
                key = (d, -abs(nx - (w - 1)) - abs(ny - (h - 1)))
                if key > best:
                    best = (key[0], dx, dy)
        return [best[1], best[2]]

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # choose action that maximizes "contesting advantage" over opponent for the best resource
        # score: favor large (opp_d - self_d), then favor closeness after advantage
        best_for_cell = -10**18
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            adv = od - sd
            score = adv * 1000 - sd  # contest when we are closer; otherwise discourage
            if score > best_for_cell:
                best_for_cell = score

        # small tie-breaker: keep away from opponent to reduce capture chances
        opp_sep = abs(nx - ox) + abs(ny - oy)
        total = best_for_cell + opp_sep * 0.01
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]