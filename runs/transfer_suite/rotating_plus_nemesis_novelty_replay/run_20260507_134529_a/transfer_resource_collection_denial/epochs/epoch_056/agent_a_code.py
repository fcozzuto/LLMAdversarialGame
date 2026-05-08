def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        # Stay unless moving closer to opponent is possible without hitting obstacles.
        bestv = -10**9
        bestm = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    # Choose move that maximizes deterministic advantage toward resources.
    # Advantage = (opp_dist - my_dist), prefer larger. Tie-break by my_dist then lexicographic move order.
    best = (-10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        # Evaluate best resource for this hypothetical next position.
        best_adv = -10**9
        best_md = 10**9
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - md
            if adv > best_adv or (adv == best_adv and md < best_md):
                best_adv, best_md = adv, md
        cand = (best_adv, -best_md, dx, dy)
        # Prefer higher adv, then lower md (encoded via -best_md), then earlier move (dx,dy order).
        if cand[0] > best[0] or (cand[0] == best[0] and cand[1] > best[1]):
            best = cand

    return [best[2], best[3]]