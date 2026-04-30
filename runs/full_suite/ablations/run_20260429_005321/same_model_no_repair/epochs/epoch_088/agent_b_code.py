def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Go to far corner but aligned with parity to reduce oscillation.
        tx, ty = (w - 1, h - 1)
        if (sx + sy) % 2 != (tx + ty) % 2:
            tx, ty = (w - 1, 0) if sy < h - 1 else (0, h - 1)
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, tx, ty)
            k = (d, dx, dy)
            if best is None or k < best[0]:
                best = (k, dx, dy)
        return [best[1], best[2]]

    # Target: resources that are currently more "reachable" for us than for opponent.
    # Score each move by (our distance improvement) + (opponent threat) + small tie-breakers.
    rlist = [(r[0], r[1]) for r in resources]
    # Precompute best distances for current position
    my_closest = min(cheb(sx, sy, rx, ry) for rx, ry in rlist)
    opp_closest = min(cheb(ox, oy, rx, ry) for rx, ry in rlist)

    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        d_self_to_nearest = min(cheb(nx, ny, rx, ry) for rx, ry in rlist)
        # Threat: closest resource we would take that opp could also take quickly.
        threat = 0
        for rx, ry in rlist:
            d_s = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            if d_s <= d_o:
                # If opponent is also competitive, penalize
                gap = d_o - d_s
                if gap <= 2:
                    threat = max(threat, 3 - gap)
        # Encourage distancing from opponent when they are close and competitive overall
        opp_dist = cheb(nx, ny, ox, oy)
        opp_pen = 0
        if opp_closest <= my_closest + 1:
            if opp_dist <= 2:
                opp_pen = 2

        # Favor moves that reduce our nearest distance; deterministic tie-breaks use move ordering.
        key = (d_self_to_nearest, threat + opp_pen, -cheb(nx, ny, sx, sy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]