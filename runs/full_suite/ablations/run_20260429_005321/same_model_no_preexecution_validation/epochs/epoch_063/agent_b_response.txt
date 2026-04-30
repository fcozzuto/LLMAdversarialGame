def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if blocked(sx, sy) or not dirs:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose best move by deterministic heuristic: maximize advantage over opponent to reach a resource,
    # penalize moving near obstacles / into dead zones.
    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        if resources and (nx, ny) in {(r[0], r[1]) for r in resources}:
            return [dx, dy]

        my_best = 10**9
        opp_best = 10**9
        adv_best = -10**18
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if md < my_best: my_best = md
            if od < opp_best: opp_best = od
            adv = od - md
            if adv > adv_best: adv_best = adv

        # Local obstacle pressure: count blocked neighbors after move
        neigh_blocked = 0
        for ex, ey in dirs:
            tx, ty = nx + ex, ny + ey
            if blocked(tx, ty):
                neigh_blocked += 1

        # Slight preference to move toward center-ish and away from staying
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        center_pref = -cheb(nx, ny, (w-1)/2.0, (h-1)/2.0)

        # Weights tuned for small deterministic policy
        score = (adv_best * 20) + (10 - my_best) + (neigh_blocked * -2) + stay_pen * -3 + int(center_pref)
        if score > best[0]:
            best = (score, dx, dy)

    if best[1] == 0 and best[2] == 0:
        # Fallback: pick any safe move deterministically preferring non-stay
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[1], best[2]]