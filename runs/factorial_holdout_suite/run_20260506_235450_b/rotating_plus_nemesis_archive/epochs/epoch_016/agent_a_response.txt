def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    move_list = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def obstacle_pen(x, y):
        pen = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nx, ny = x + ax, y + ay
            if (nx, ny) in obstacles:
                pen += 2
        return pen

    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    res_set = [(r[0], r[1]) for r in resources]
    if not res_set:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None; bestv = -10**9
        for dx, dy in move_list:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -cheb(nx, ny, tx, ty) - obstacle_pen(nx, ny)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    best = None; bestv = -10**18
    for dx, dy in move_list:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_best = 10**9; opp_best = 10**9; their_res = None
        for rx, ry in res_set:
            myd = cheb(nx, ny, rx, ry)
            if myd < my_best:
                my_best = myd
                their_res = (rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if opd < opp_best:
                opp_best = opd
        # Primary: get to some resource sooner; Secondary: deny by shrinking gap to nearest target relative to opponent.
        gap = (opp_best - my_best)
        # Small bias to avoid hugging obstacles.
        v = (gap * 3.0) - (my_best * 1.2) - obstacle_pen(nx, ny) + (-0.05 * cheb(nx, ny, ox, oy))
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [best[0], best[1]] if best else [0, 0]