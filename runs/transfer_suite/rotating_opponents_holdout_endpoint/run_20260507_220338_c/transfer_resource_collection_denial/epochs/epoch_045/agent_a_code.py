def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    # Pick top candidate resources relative to opponent, but weighted toward those we can reach first.
    cand = []
    for rx, ry in resources:
        myd0 = cheb(sx, sy, rx, ry)
        opd0 = cheb(ox, oy, rx, ry)
        # Prefer: we can arrive sooner; also prefer closer targets overall.
        base = (opd0 - myd0) * 100 - myd0
        cand.append((base, myd0, opd0, rx, ry))
    cand.sort(reverse=True)
    top = cand[:6]

    best = (0, 0); best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        # Immediate desirability and contest pressure
        for base, myd0, opd0, rx, ry in top:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Strongly prefer moves that make us strictly earlier for some resource.
            # Slightly prefer moves that also slow down opponent (by reducing our distance).
            lead = (opd - myd)
            val += lead * 120 - myd * 6

            # Big bonus if we'd land on a resource cell.
            if (nx, ny) == (rx, ry):
                val += 10**6

        # If we're about to be blocked from improving, reduce aimless moves by preferring
        # progress toward the best candidate by Manhattan-ish sign.
        if top:
            _, _, _, rx, ry = top[0]
            sgnx = 0 if nx == rx else (1 if nx < rx else -1)
            sgny = 0 if ny == ry else (1 if ny < ry else -1)
            val += (dx == sgnx) * 8 + (dy == sgny) * 8

        # Deterministic tie-breaker: prefer staying still only if equal.
        if val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]