def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a resource where we have a capture advantage in distance vs opponent.
    best_res = resources[0]
    best_margin = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        margin = (opd - myd) * 1000 - myd  # strongly prefer advantage; tie-break closer
        if margin > best_margin:
            best_margin = margin
            best_res = (rx, ry)

    rx, ry = best_res

    # If a resource is directly reachable next, grab it deterministically if it exists.
    occupied = set(tuple(rp) for rp in resources)
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) in occupied:
            # immediate collection: extremely high priority
            myd_after = 0
            opd_after = cheb(ox, oy, nx, ny)
            score = 10**12 + (opd_after - myd_after)
        else:
            # Otherwise, move to reduce my distance to target while increasing opp distance to same target.
            myd_after = cheb(nx, ny, rx, ry)
            opd_after = cheb(ox, oy, rx, ry)
            # Small lookahead: if we move closer to another resource with advantage, allow it.
            best_alt = 0
            for arx, ary in resources:
                if (arx, ary) == (rx, ry):
                    continue
                alt_m = cheb(ox, oy, arx, ary) - cheb(nx, ny, arx, ary)
                if alt_m > best_alt:
                    best_alt = alt_m
            score = (best_margin - myd_after * 3) + (opd_after * 0.5) + best_alt * 10
        # Deterministic tie-break: prefer lower dx then lower dy then staying
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]