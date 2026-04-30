def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestd = 10**9
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, cx, cy)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Deterministic tie-breaking: fixed resource order
    resources_sorted = sorted(resources, key=lambda r: (r[0], r[1]))

    best_move = (0, 0)
    best_val = -10**18

    # Identify resources where opponent is currently closer (for defense/intercept)
    opp_leads = []
    for rx, ry in resources_sorted:
        if (rx, ry) in obstacles:
            continue
        opd0 = cheb(ox, oy, rx, ry)
        myd0 = cheb(sx, sy, rx, ry)
        if opd0 < myd0:
            opp_leads.append((opd0 - myd0, opd0, rx, ry))
    opp_leads.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    defend_targets = opp_leads[:2]  # at most 2 deterministic intercept targets

    for dx, dy, nx, ny in legal:
        val = 0
        # Main objective: resources we can reach strictly earlier than opponent
        for rx, ry in resources_sorted:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd < opd:
                val += 20 - myd  # prefer closer winning resources
            elif myd == opd:
                val += 4 - myd   # encourage ties (often better than losing)
            else:
                val -= 0.5 * myd # mild penalty for moving toward contested/losing ones

        # Defensive/intercept: if opponent leads, reduce our distance to their best lead(s)
        for _, _, tx, ty in defend_targets:
            val += (12 - cheb(nx, ny, tx, ty)) * 0.7

        # Small preference for moving toward center to avoid stalling near edges
        cx, cy = (w - 1) // 2, (h - 1) // 2
        val += (6 - cheb(nx, ny, cx, cy)) * 0.05

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[