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

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestv = -10**18
        best = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if -d > bestv:
                bestv = -d
                best = [dx, dy]
        return best

    bestv = -10**18
    best = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = -1
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd < opd:
                v = 100 - myd - opd // 2
            elif myd == opd:
                v = 30 - myd
            else:
                v = - (myd - opd) - myd // 3
            if v > score:
                score = v
        # Small tie-break: prefer moves that also reduce opponent distance to the same best resource
        tie = 0
        if score > bestv:
            bestv = score
            best = [dx, dy]
        elif score == bestv:
            # compute minimal my distance to any resource that I can reach no later than opponent
            best_t = 10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                if myd <= opd and myd < best_t:
                    best_t = myd
            best2 = best
            ox2, oy2 = ox, oy
            bx, by = sx + best2[0], sy + best2[1]
            bt = 10**18
            for rx, ry in resources:
                myd = cheb(bx, by, rx, ry)
                opd = cheb(ox2, oy2, rx, ry)
                if myd <= opd and myd < bt:
                    bt = myd
            if best_t < bt:
                best = [dx, dy]
    return best