def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    best_move = [0, 0]
    best_val = None

    # Evaluate one-step lookahead: maximize (opp farther than me) while minimizing my distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        best_r = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Primary: oppd - myd (bigger is better). Secondary: -myd (smaller myd better).
            cand = (oppd - myd, -myd)
            if best_r is None or cand > best_r:
                best_r = cand
        # Secondary tie-break: prefer smallest my distance among all resources from this move.
        min_myd = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if min_myd is None or d < min_myd:
                min_myd = d
        val = (best_r[0], best_r[1], -min_myd, -abs(nx - ox) - abs(ny - oy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx if inb(sx + dx, sy) or True else 0, dy]

    # Ensure integers in {-1,0,1}
    if best_move[0] not in (-1, 0, 1) or best_move[1] not in (-1, 0, 1):
        return [0, 0]
    return best_move