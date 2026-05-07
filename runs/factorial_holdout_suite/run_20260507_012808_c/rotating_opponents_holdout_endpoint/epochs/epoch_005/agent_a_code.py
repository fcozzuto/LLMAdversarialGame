def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick promising targets: where we are not farther than opponent (tie-break friendly).
    best_targets = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds <= do:
            lead = do - ds
            # favor closer to us among same lead
            best_targets.append((lead, -ds, rx, ry))
    best_targets.sort(reverse=True)
    if not best_targets:
        # fallback: chase the single resource with maximum advantage
        best_targets = [max(resources, key=lambda r: cheb(ox, oy, r[0], r[1]) - cheb(sx, sy, r[0], r[1]))]
        targets = best_targets if isinstance(best_targets[0], tuple) else [(0, 0, best_targets[0][0], best_targets[0][1])]
    targets = best_targets[:3]
    if targets and isinstance(targets[0], tuple):
        tlist = [(t[2], t[3]) for t in targets]
    else:
        tlist = [(best_targets[0][0], best_targets[0][1])]

    # Precompute resource set for quick stepping bonus
    rset = set(tuple(r) for r in resources)

    opp_adj_pen = 2  # discourage moving into opponent's immediate neighborhood
    wall_pen = 0

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            # Avoid giving away: if opponent is adjacent, prefer moves that increase distance
            opp_d = cheb(nx, ny, ox, oy)
            adj = 1 if opp_d <= 1 else 0

            # Race value: maximize opponent-self distance advantage to closest promising target
            best_val = -10**9
            for rx, ry in tlist:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                val = (do - ds)  # positive means we are closer than opponent to that target
                # if we step onto the resource now, dominate
                if (nx, ny) == (rx, ry):
                    val += 100
                # also prefer smaller distance when equally advantaged
                val -= 0.1 * ds
                if val > best_val:
                    best_val = val

            step_bonus = 1 if (nx, ny) in rset else 0
            cand.append((best_val + 0.5 * step_bonus - opp_adj_pen * adj - wall_pen, dx, dy))

    cand.sort(reverse=True)
    return [cand[0][1], cand[0][2]]