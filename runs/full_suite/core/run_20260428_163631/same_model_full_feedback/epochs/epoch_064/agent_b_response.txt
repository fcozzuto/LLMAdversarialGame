def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_d = cheb(sx, sy, ox, oy)

    if not resources:
        # Deterministic avoidance / drift
        best = (0, 0)
        best_sc = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            nd = cheb(nx, ny, ox, oy)
            sc = nd * 10 - (abs((nx - ox)) + abs((ny - oy)))
            if nd <= 1: sc -= 20
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]]

    # Score candidate by choosing a resource where we are relatively closer than opponent
    best = (0, 0)
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Avoid stepping adjacent to opponent when possible
        nd_opp = cheb(nx, ny, ox, oy)
        penalty = 0
        if nd_opp <= 1:
            penalty = 50
        # Best relative advantage across remaining resources
        best_adv = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Favor taking resources sooner and where opponent is slower
            adv = (opd - myd) * 6 - myd
            # Slight bias to not overcommit to very long distances
            adv -= 2 * (myd > 6)
            if adv > best_adv:
                best_adv = adv
        # If opponent is close, also include a small chase/block term to deny nearest resource
        sc = best_adv - penalty
        if opp_d <= 3:
            sc += (cheb(nx, ny, ox, oy) <= opp_d) * 1
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]