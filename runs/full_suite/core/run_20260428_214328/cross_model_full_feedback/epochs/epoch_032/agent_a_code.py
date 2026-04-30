def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obst = set((int(p[0]), int(p[1])) for p in obstacles)
    res = [(int(p[0]), int(p[1])) for p in resources]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not res:
        # Default: maximize separation from opponent (safer than repeating resource policy)
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    # Choose target resource where we can get the biggest advantage, then move accordingly.
    # Advantage = (opp_dist - self_dist). Prefer positive.
    best_target = None
    best_adv = -10**9
    for rx, ry in res:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # Slightly prefer closer-than-opponent targets even if tied.
        if adv > best_adv or (adv == best_adv and sd < cheb(sx, sy, best_target[0], best_target[1]) if best_target else True):
            best_adv = adv
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = None
    best_val = -10**9
    for dx, dy, nx, ny in legal:
        self_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        new_adv = opp_d - self_d

        # Also steer away from opponent to prevent them contesting another resource path.
        sep = cheb(nx, ny, ox, oy)

        # If opponent is currently closer to this target, prioritize moves that break their line:
        # move to reduce our distance more aggressively.
        urgency = 2 if cheb(sx, sy, rx, ry) > cheb(ox, oy, rx, ry) else 1

        # Secondary: avoid moving too close to any resource where opponent might steal next.
        opp_steal_risk = 0
        for rr_x, rr_y in res:
            od2 = cheb(ox, oy, rr_x, rr_y)
            sd2 = cheb(nx, ny, rr_x, rr_y)
            if od2 <= sd2:
                risk = (3 - (od2 - sd2))  # higher when opponent is not worse
                if risk > opp_steal_risk:
                    opp_steal_risk = risk

        val = 100 * new_adv + (3 * sep) - (5 * opp_steal_risk) - (urgency * self_d)
        # Small deterministic tie-break: prefer moves with smaller dx/dy magnitude, then lex order.
        if val > best_val or (val == best_val and (abs(dx)+abs(dy), dx, dy) < (abs(best_move[0])+abs(best_move[1]), best_move[0], best_move[1]) if best_move else True):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]