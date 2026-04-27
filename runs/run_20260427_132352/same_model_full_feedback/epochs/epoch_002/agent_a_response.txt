def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        # Default: drift away while staying roughly toward center to reduce opponent pressure.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0); bestv = -10**9
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): continue
            if (nx, ny) in obstacles: continue
            v = -cheb(nx, ny, ox, oy) - 0.3 * cheb(nx, ny, tx, ty)
            if v > bestv: bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Score a position: prefer resources where we have advantage; otherwise deny those opponent targets.
    best = (0, 0); bestv = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): continue

        # If we step onto obstacle, engine will keep us in place; heavily penalize.
        if (nx, ny) in obstacles:
            v = -10**12
        else:
            min_opp = 10**9
            best_adv = -10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles: 
                    continue
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                adv = d_op - d_me
                if adv > best_adv: best_adv = adv
                if d_op < min_opp: min_opp = d_op

            # Main term: advantage to capture; secondary: deny by increasing opponent distance to closest resource.
            # Tertiary: avoid opponent when we cannot secure advantage.
            v = 2000 * best_adv - min_opp
            d_after_opp = cheb(nx, ny, ox, oy)
            if best_adv <= 0:
                v += 80 * d_after_opp
            else:
                v += 5 * d_after_opp
            # Mild center bias for stability
            cx, cy = (w - 1) // 2, (h - 1) // 2
            v -= 0.01 * cheb(nx, ny, cx, cy)

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]