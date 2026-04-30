def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2): 
        dx = x1 - x2; dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)
    def man(x1, y1, x2, y2): return abs(x1-x2) + abs(y1-y2)

    # If stuck/unusable (rare), just stay.
    if not valid(sx, sy):
        return [0, 0]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dO = cheb(nx, ny, ox, oy)
            score = (dO, -man(nx, ny, ox, oy))
            cand = (score, dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[1], best[2]] if best else [0, 0]

    # Pick target resource by estimated advantage (opponent reach time vs ours).
    bestR = None
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; else deny proximity.
        adv = dO - dS
        density = 0
        for rx2, ry2 in resources:
            if (rx2, ry2) != (rx, ry):
                if cheb(rx, ry, rx2, ry2) <= 1:
                    density += 1
        score = (adv, -dS, density)
        if bestR is None or score > bestR[0]:
            bestR = (score, rx, ry)
    _, tx, ty = bestR

    # Move toward target; avoid positions that let opponent become significantly closer to it.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dS2 = cheb(nx, ny, tx, ty)
        dO2 = cheb(ox, oy, tx, ty)
        opp_closer = (dO2 - dS2)  # positive = we are closer than opp (as of next step)
        distToOpp = cheb(nx, ny, ox, oy)

        # Primary: reduce distance to target.
        # Secondary: keep/extend advantage vs opponent for target.
        # Tertiary: keep away from opponent.
        score = (-dS2, opp_closer, distToOpp, -abs(dx), -abs(dy))
        cand = (score, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[1], best[2]] if best else [0, 0]