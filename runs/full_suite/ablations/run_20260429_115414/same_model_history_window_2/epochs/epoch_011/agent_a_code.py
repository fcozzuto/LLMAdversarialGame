def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # If no resources, move deterministically toward center with mild opponent avoidance.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0); bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            myc = cheb(nx, ny, cx, cy)
            odis = cheb(nx, ny, ox, oy)
            v = -myc * 2 + odis * 0.15
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Evaluate next move by best immediate resource contest outcome.
    best = (0, 0); bestv = -10**18
    my_d0 = cheb(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): 
            continue
        best_res = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            if not legal(rx, ry): 
                continue
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are strictly closer; otherwise deny by approaching soonest-losing threats.
            win_gap = od - myd  # positive => we can get first (earlier or tie)
            tie_bias = -0.05 * myd
            # If opponent is close but we aren't, slightly weight moving to reduce their lead.
            urgency = -0.01 * abs((rx + ry) - (nx + ny))
            score = win_gap * 3.0 + tie_bias + urgency
            if score > best_res:
                best_res = score
        # Small safety shaping: avoid stepping closer to opponent when contest is equal-ish.
        # Also keep movement reasonable toward some contest.
        o_after = cheb(nx, ny, ox, oy)
        closeness_pen = 0.08 * (my_d0 - o_after)
        v = best_res - closeness_pen
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]