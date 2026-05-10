def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    role = (observation.get("self_role", "") or "").lower()

    deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def freedom(x, y):
        c = 0
        for ddx, ddy in deltas:
            nx, ny = x + ddx, y + ddy
            if valid(nx, ny):
                c += 1
        return c

    def corner_bias(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestd = -1
        for cx, cy in corners:
            d = (cx - x) * (cx - x) + (cy - y) * (cy - y)
            if d > bestd:
                bestd = d
        return bestd

    pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role)

    best = [0, 0]
    if pursuer:
        # Pursue: minimize distance; prefer more freedom when tied; prefer earlier deltas deterministically.
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny)
            f = freedom(nx, ny)
            score = ( -d, f, -abs(nx - ox) - abs(ny - oy) )
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]
    else:
        # Evade: maximize distance; avoid being boxed via freedom; move toward farthest corner when safe.
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny)
            f = freedom(nx, ny)
            cb = corner_bias(nx, ny)
            score = (d, f, cb, -abs(nx - ox) - abs(ny - oy))
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]

    return [int(best[0]), int(best[1])]