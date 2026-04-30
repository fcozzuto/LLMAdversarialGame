def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        # Pick resource with best "temporal advantage": (opp_dist - our_dist),
        # slight bias toward earlier grid order for determinism.
        best = None
        best_score = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            # If we are tied/close, prefer the one we can reach strictly earlier (adv) and then lower coord.
            score = adv * 1000 + (3 - ds)  # higher better
            if score > best_score or (score == best_score and (rx, ry) < best):
                best_score = score
                best = (rx, ry)

        tx, ty = best
        # Score candidate moves: move closer to target, avoid obstacles, and reduce opponent's threat.
        best_move = (0, 0); best_val = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            ds2 = cheb(nx, ny, tx, ty)
            do2 = cheb(ox, oy, tx, ty)
            # Prefer reducing our distance; if equal, prefer increasing opponent distance.
            v = (cheb(sx, sy, tx, ty) - ds2) * 10 - (do2 - cheb(ox, oy, tx, ty)) * 1
            # Small bias to avoid getting boxed: count free adjacent cells.
            free = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0: 
                        continue
                    ax, ay = nx + adx, ny + ady
                    if inb(ax, ay) and (ax, ay) not in obstacles:
                        free += 1
            v += free * 0.05
            # Deterministic tie-break: lowest (dx,dy) in lexicographic order.
            cand = (v, -dx, -dy)
            best_c = (best_val, -best_move[0], -best_move[1])
            if cand > best_c:
                best_val = v
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: keep pressure by moving toward center-ish while avoiding obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0); best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, cx, cy)
        v = -d
        cand = (v, -dx, -dy)
        best_c = (best_val, -best_move[0], -best_move[1])
        if cand > best_c:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]