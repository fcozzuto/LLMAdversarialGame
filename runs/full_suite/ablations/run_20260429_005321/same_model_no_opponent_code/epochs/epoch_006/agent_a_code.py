def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obst = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obst

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def free_neighbors_score(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny):
                    c += 1
        return c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            v = free_neighbors_score(nx, ny)
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            if d1 < my_best:
                my_best = d1
            if d2 < opp_best:
                opp_best = d2
        # Prefer resources we are currently closer to; otherwise still reduce distance.
        # Also keep some mobility and avoid moves that land adjacent to many obstacles.
        adj_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) in obst:
                    adj_obs += 1
        v = 0
        v += (opp_best - my_best) * 2.0
        v += -my_best * 0.6
        v += free_neighbors_score(nx, ny) * 0.15
        v += -adj_obs * 0.3

        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]
    return best