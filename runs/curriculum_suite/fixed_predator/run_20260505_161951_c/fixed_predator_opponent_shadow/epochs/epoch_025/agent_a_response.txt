def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    if not resources:
        # Deterministic: move to maximize separation from opponent (deny interception)
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = (abs(nx - ox) + abs(ny - oy)) - 0.001 * (nx + ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Evaluate moves by: pick resource that we can secure sooner than opponent after our move.
    # Score = our_dist_improvement - opponent_advantage + small tie-breakers for determinism.
    best_move = None
    best_score = -10**18
    # Also add a "centering" pressure to reduce oscillation / improve pathing.
    cx, cy = (gw - 1) / 2.0, (gh - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # compute our best target advantage within 2-step horizon (cheap, deterministic)
        local_best = -10**18
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # We "want" resources where opponent is farther than us after we move.
            # Encourage grabbing (small d_self), penalize being behind.
            # Large bonus if d_self < d_opp (we're ahead), scaled by margin.
            if d_self == 0:
                ahead_bonus = 2000
            else:
                ahead_bonus = 0
            margin = d_opp - d_self
            adv = margin * 30 - d_self * 2 + ahead_bonus
            # secondary: prefer resources closer to center once tied
            adv -= 0.01 * (abs(rx - cx) + abs(ry - cy))
            if adv > local_best:
                local_best = adv
        # Final move score also prefers moving toward the best target area and away from corner stagnation
        center_pen = 0.05 * (abs(nx - cx) + abs(ny - cy))
        opp_close_pen = 0.02 * (abs(nx - ox) + abs(ny - oy))
        total = local_best - center_pen - opp_close_pen + 0.001 * (nx - sx) + 0.0005 * (ny - sy)
        if total > best_score:
            best_score = total
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]