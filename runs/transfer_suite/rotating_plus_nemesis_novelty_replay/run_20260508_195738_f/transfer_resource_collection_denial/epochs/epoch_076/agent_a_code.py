def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (0, 0) if ((ox + oy) & 1) == 0 else (w - 1, h - 1)
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Interception-style: pick move that maximizes "who is closer" advantage
    # over the best available resource.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Prefer not to let opponent get the best resource uncontested.
        # Take max over resources of (opp_d - self_d); add small pressure for reducing self distance.
        best_adv = -10**18
        best_self_d = 10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv:
                best_adv = adv
                best_self_d = sd
            elif adv == best_adv and sd < best_self_d:
                best_self_d = sd

        # Encourage moving into positions that reduce our distance to the "winning" resource,
        # and slightly avoid edging toward the opponent.
        opp_dist = cheb(nx, ny, ox, oy)
        v = best_adv * 1000 - best_self_d + 0.01 * opp_dist
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best