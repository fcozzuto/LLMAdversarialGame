def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestv = -10**9; best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = -cheb(nx, ny, cx, cy) * 2 + cheb(nx, ny, ox, oy) * 0.1
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    bestv = -10**18; best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): 
            continue
        my_best = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            if not legal(rx, ry): 
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we can get there no later than opponent (in chebyshev steps)
            # Encourage immediate grabs and avoid moves that only help if we can't get there first.
            score = adv * 10 + (2 if sd == 0 else 0) - (sd == 0 and od == 0)
            if sd > od:  # if opponent closer, strongly discourage
                score -= (sd - od) * 20
            if score > my_best:
                my_best = score
        # Small tie-break to keep deterministic, slightly favor staying mobile toward closer resources.
        tie = -cheb(nx, ny, resources[0][0], resources[0][1]) * 0.001
        v = my_best + tie
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]