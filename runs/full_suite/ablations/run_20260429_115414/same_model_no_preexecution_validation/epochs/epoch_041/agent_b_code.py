def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # If no resources, just drift toward center while not walking into walls/obstacles.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestm = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, cx, cy) - 0.5 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # Innovation: score each candidate move by the BEST resource we could secure next-turn advantage for,
    # plus an opponent-evade term when they are close.
    opp_close = cheb(sx, sy, ox, oy) <= 1
    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Basic safety: discourage stepping adjacent to opponent when not strongly beneficial.
        sd_opp = cheb(nx, ny, ox, oy)
        evade = 0.0
        if opp_close or sd_opp <= 1:
            evade = (sd_opp - 1) * 3.0  # prefer moving away when we're close

        # Resource advantage for this move (lookahead one step).
        best_adv = -10**18
        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Want large oppd - selfd (we're closer). Penalize being far; reward being strictly closer.
            adv = (oppd - selfd) * 4.0 - selfd * 0.35
            # If we're currently not closer, reduce unless it gives major swing.
            if selfd >= oppd:
                adv -= (selfd - oppd) * 1.2
            if adv > best_adv:
                best_adv = adv
        # Tie-break deterministically by preferring moves that reduce distance to the best target.
        v = best_adv + evade
        if v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]