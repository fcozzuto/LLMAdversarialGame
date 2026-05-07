def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cells(v):
        out = []
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    out.append((x, y))
        return out

    obstacles = set(cells(observation.get("obstacles")))
    resources = [p for p in cells(observation.get("resources")) if p not in obstacles]
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Heuristic: pick move maximizing (advantage to best target) and "denial" (make it harder for opponent)
    # We approximate by comparing my distance after move vs opponent distance now, and also my distance vs opponent's best.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best = 10**9
        opp_best = 10**9
        # compute opponent's current best target distance baseline
        for rx, ry in resources:
            d = abs(rx - ox) + abs(ry - oy)
            if d < opp_best:
                opp_best = d

        score = -0.0
        score_best = -10**18
        for rx, ry in resources:
            my_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)

            if my_d < my_best:
                my_best = my_d

            # Advantage: prefer targets I can reach sooner than opponent
            adv = (opp_d - my_d)

            # Denial: if I can reach a target significantly sooner than opponent, it reduces their options
            deny = adv

            # Tie-break: slightly prefer closer-than-opponent overall and central-ish progress
            closeness = -my_d
            total = 2.2 * adv + 0.9 * deny + 0.1 * closeness
            if total > score_best:
                score_best = total

        # Small bias to avoid stalling when advantage is similar
        score = score_best - 0.05 * (abs(dx) + abs(dy))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]