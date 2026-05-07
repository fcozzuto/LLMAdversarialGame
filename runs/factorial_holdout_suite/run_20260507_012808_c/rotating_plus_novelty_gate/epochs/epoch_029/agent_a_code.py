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
    if not valid(sx, sy):
        sx = max(0, min(w - 1, sx))
        sy = max(0, min(h - 1, sy))

    if not resources or w <= 0 or h <= 0:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bestd = -10**18
        bestm = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = -cheb(nx, ny, tx, ty)
            if d > bestd:
                bestd = d
                bestm = [dx, dy]
        return bestm

    def best_value(px, py):
        bestv = -10**18
        bestopp = 10**18
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Strongly prefer winning capture first, otherwise minimize our arrival time.
            # Tie-break: also prefer positions that are hard for opponent to reach (larger opd).
            win = opd - myd
            v = win * 10 + (-myd)
            if win < 0:
                v = v - (abs(win) * 4)  # discourage losing races, but still allow progress
            if myd == 0:
                v += 1000
            if (v > bestv) or (v == bestv and opd < bestopp):
                bestv = v
                bestopp = opd
        # Add slight pressure toward/away from opponent depending on whether we can contest.
        can_contest = any(cheb(px, py, r[0], r[1]) <= cheb(ox, oy, r[0], r[1]) for r in resources)
        md = cheb(px, py, ox, oy)
        bestv += (-md if can_contest else md) * 0.05
        return bestv

    bestv = -10**18
    bestm = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = best_value(nx, ny)
        # Deterministic tie-break: prefer staying still last, then x, then y.
        if v > bestv or (v == bestv and (dx, dy) < (bestm[0], bestm[1])):
            bestv = v
            bestm = [dx, dy]
    return bestm