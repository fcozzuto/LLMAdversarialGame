def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    sr = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("pred" in sr) or (sr == "pursuer")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def obstacle_risk(x, y):
        if (x, y) in obs:
            return 10**9
        r = 0
        for ex, ey in obs:
            dx, dy = x - ex, y - ey
            d2 = dx * dx + dy * dy
            if d2 == 0:
                return 10**9
            if d2 <= 9:
                r += (10 - d2)  # stronger near obstacles
        return r

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        d2 = dist2(nx, ny)
        risk = obstacle_risk(nx, ny)
        if pursuer:
            val = (-d2) - 0.7 * risk
            tie = (-risk, d2)
        else:
            val = (d2) - 0.9 * risk
            tie = (risk, -d2)
        # Deterministic tie-breaker: prefer capture for pursuer, otherwise max/min distance then low risk then lexicographic move
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            if pursuer:
                cand1 = (dist2(nx, ny) == 0, -risk, d2, dx, dy)
                bestx, besty = best
                bx, by = sx + bestx, sy + besty
                bestcand = (dist2(bx, by) == 0, -(obstacle_risk(bx, by)), dist2(bx, by), bestx, besty)
                if cand1 > bestcand:
                    best = (dx, dy)
            else:
                cand1 = (-dist2(nx, ny), -risk, dx, dy)
                bestx, besty = best
                bx, by = sx + bestx, sy + besty
                bestcand = (-dist2(bx, by), -(obstacle_risk(bx, by)), bestx, besty)
                if cand1 > bestcand:
                    best = (dx, dy)

    if best is None:
        # fallback: stay put if all moves blocked (should be rare)
        return [0, 0]
    return [best[0], best[1]]