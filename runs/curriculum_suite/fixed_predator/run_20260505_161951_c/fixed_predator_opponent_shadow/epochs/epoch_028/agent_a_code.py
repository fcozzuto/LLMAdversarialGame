def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    if not resources:
        # defensive: drift toward the line between us and opponent to contest mid-grid
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            d = man(nx, ny, tx, ty)
            key = (d, man(nx, ny, ox, oy))
            if bestv is None or key < bestv:
                bestv = key
                best = (dx, dy)
        return [best[0], best[1]]

    # 1-step lookahead: pick move that maximizes (opp_dist - self_dist) to the best resource we could contest
    best_move = (0, 0)
    best_score = -10**18
    best_second = -10**18

    for dx, dy, nx, ny in moves:
        # small tie-break: prefer moves that reduce distance to opponent to enable shadow/contest
        max_adv = -10**18
        min_opp_after = 10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer (good contest)
            if adv > max_adv:
                max_adv = adv
                min_opp_after = od
            elif adv == max_adv and od < min_opp_after:
                min_opp_after = od

        # also discourage stepping away from the best contested resource when behind
        # (if adv negative, choosing the least negative is better)
        opp_closer_penalty = -min_opp_after * 0.001  # prefer resources nearer to opponent (they'll be pressured)
        score = max_adv + opp_closer_penalty
        # secondary: prefer moves that increase our distance lead toward the contested resource (or reduce loss)
        second = -man(nx, ny, ox, oy)

        if score > best_score or (score == best_score and second > best_second):
            best_score = score
            best_second = second
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]