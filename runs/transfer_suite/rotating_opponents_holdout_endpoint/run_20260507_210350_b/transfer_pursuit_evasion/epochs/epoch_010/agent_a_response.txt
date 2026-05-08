def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def near_obst(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    c += 1
        return c
    self_role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in self_role) or ("hunter" in self_role) or ("chaser" in self_role)
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    bestv = -10**18 if pursuer else 10**18
    curd = cheb(sx, sy, ox, oy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        nd = cheb(nx, ny, ox, oy)
        no = near_obst(nx, ny)
        # ties broken deterministically by move order and value
        if pursuer:
            v = (curd - nd) * 20 - no * 3 - cheb(nx, ny, (w - 1) / 2, (h - 1) / 2) * 0.01
            # prefer not to stall
            if nd >= curd:
                v -= 0.5
            if v > bestv:
                bestv = v
                best_move = [dx, dy]
        else:
            v = (nd - curd) * 20 - no * 3 + cheb(nx, ny, (w - 1) / 2, (h - 1) / 2) * 0.01
            if nd <= curd:
                v -= 0.5
            if v < bestv:
                bestv = v
                best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]