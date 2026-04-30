def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_cost(x, y):
        if not inb(x, y): return 10**7
        if (x, y) in obstacles: return 10**6
        c = 0
        for nx in (x - 1, x, x + 1):
            for ny in (y - 1, y, y + 1):
                if (nx, ny) in obstacles: c += 2
        return c

    def best_resource_target():
        if not resources:
            return ((w - 1) // 2, (h - 1) // 2)
        # Choose resource with highest (opp_dist - self_dist) advantage; tie-break by nearest to us.
        best = resources[0]
        best_score = cheb(ox, oy, best[0], best[1]) - cheb(sx, sy, best[0], best[1])
        best_dist = cheb(sx, sy, best[0], best[1])
        for rx, ry in resources[1:]:
            sc = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
            ds = cheb(sx, sy, rx, ry)
            if sc > best_score or (sc == best_score and ds < best_dist) or (sc == best_score and ds == best_dist and (rx, ry) < best):
                best_score, best_dist, best = sc, ds, (rx, ry)
        return best

    tx, ty = best_resource_target()
    best_move = (0, 0)
    best_val = -10**30

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        od = cheb(ox, oy, tx, ty)
        nd = cheb(nx, ny, tx, ty)
        # Value: maximize advantage (opp_dist - self_dist), then prefer shorter self_dist, avoid obstacles.
        val = (od - nd) * 1000 - nd - obst_cost(nx, ny) * 10
        # If we are exactly on the best target, strongly prefer it.
        if (nx, ny) == (tx, ty):
            val += 10**6
        # If closer than opponent by margin, prefer.
        if nd + 1 < od:
            val += 200
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]