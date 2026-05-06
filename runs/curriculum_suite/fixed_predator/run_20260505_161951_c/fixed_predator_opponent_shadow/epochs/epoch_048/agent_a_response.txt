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

    # No resources: contest midline but also keep away from immediate proximity to opponent
    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            dtx = man(nx, ny, tx, ty)
            do = man(nx, ny, ox, oy)
            # prefer reaching midline; slight penalty if too close to opponent
            v = (dtx, -do)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose target resource where we have the best advantage (opp later than us)
    best_target = None
    best_adv = None
    for rx, ry in resources:
        our_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        # advantage: bigger is better; tie-break to nearer resources for determinism
        adv = (opp_d - our_d, -our_d, rx, ry)
        if best_adv is None or adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    rx, ry = best_target
    # One-step lookahead toward the chosen target maximizing relative arrival margin after the move
    best = (0, 0)
    bestv = None
    for dx, dy, nx, ny in moves:
        our_after = man(nx, ny, rx, ry)
        opp_now = man(ox, oy, rx, ry)
        # relative margin after our move; primary objective is to increase (opp - our)
        margin = (opp_now - our_after)
        # if margin ties, prefer closer to target and farther from opponent (reduce contest loss)
        v = (-margin, our_after, man(nx, ny, ox, oy), dx, dy)
        if bestv is None or v < bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]