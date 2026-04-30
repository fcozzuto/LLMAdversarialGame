def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((int(x), int(y)))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (int(x), int(y)) not in obs:
                resources.append((int(x), int(y)))
    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    candidates = [(dx, dy) for dy in dys for dx in dxs]
    if not resources:
        tx, ty = (w // 2, h // 2) if (sx, sy) != (w // 2, h // 2) else (ox, oy)
        best = None
        bestc = 10**18
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obs:
                continue
            dist = abs(nx - tx) + abs(ny - ty)
            opp = abs(nx - ox) + abs(ny - oy)
            cost = dist + 0.15 * opp
            if cost < bestc:
                bestc = cost
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a small set of promising resources for local scoring
    scored = []
    for r in resources:
        d_s = cheb(sx, sy, r[0], r[1])
        d_o = cheb(ox, oy, r[0], r[1])
        # Prefer resources where we are likely closer than opponent
        scored.append((d_s - d_o, d_s, r[0], r[1]))
    scored.sort()
    top = [ (t[2], t[3]) for t in scored[:6] ]

    best_move = (0, 0)
    best_cost = 10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        # Encourage moving toward a resource where opponent is not closer
        total = 0.0
        for rx, ry in top:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If opponent is closer, strongly penalize; else reward closeness
            if do < ds:
                total += (do - ds + 1) * 5.0
            else:
                total += ds * 1.0
        # Mild anti-stall: if resources exist, avoid staying if another move ties closely
        stay_pen = 0.6 if (dx == 0 and dy == 0) else 0.0
        # Slightly reduce letting opponent cut through our path
        opp_press = 0.05 * cheb(nx, ny, ox, oy)
        cost = total + stay_pen + opp_press
        if cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]