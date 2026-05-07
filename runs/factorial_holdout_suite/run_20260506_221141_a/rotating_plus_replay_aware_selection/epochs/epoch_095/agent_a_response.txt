def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move, best_val = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): continue
        local_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gain = do - ds  # positive means we can arrive sooner (or tie)
            # prefer collecting while also keeping options open
            v = gain * 100 - ds
            if v > local_best:
                local_best = v
        # slight bias toward staying away from obstacles by preferring cells with more legal neighbors
        neigh = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if legal(tx, ty): neigh += 1
        local_best += neigh
        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]