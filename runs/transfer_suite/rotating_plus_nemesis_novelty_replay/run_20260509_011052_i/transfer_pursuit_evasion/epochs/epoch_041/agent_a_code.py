def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_val = -10**18 if pursuer else 10**18

    def resource_bias(x, y):
        if not resources:
            return 0
        d = None
        for rx, ry in resources:
            cd = cheb(x, y, rx, ry)
            if d is None or cd < d:
                d = cd
        # pursuer prefers closer resources, evader prefers farther
        return -d if pursuer else d

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        if nx == ox and ny == oy:
            d_after = 0
        else:
            if pursuer:
                # opponent is evader: choose their move to maximize distance from our next position
                max_d = -10**18
                for edx, edy in dirs:
                    ex, ey = ox + edx, oy + edy
                    if not valid(ex, ey):
                        continue
                    d = cheb(ex, ey, nx, ny)
                    if d > max_d:
                        max_d = d
                d_after = max_d
                val = -d_after * 1000 + resource_bias(nx, ny)
                if val > best_val:
                    best_val = val; best = [dx, dy]
            else:
                # self is evader: opponent is pursuer: choose their move to minimize distance to our next position
                min_d = 10**18
                for pdx, pdy in dirs:
                    px, py = ox + pdx, oy + pdy
                    if not valid(px, py):
                        continue
                    d = cheb(px, py, nx, ny)
                    if d < min_d:
                        min_d = d
                d_after = min_d
                val = d_after * 1000 + resource_bias(nx, ny)
                if val < best_val:
                    best_val = val; best = [dx, dy]

    return [int(best[0]), int(best[1])]