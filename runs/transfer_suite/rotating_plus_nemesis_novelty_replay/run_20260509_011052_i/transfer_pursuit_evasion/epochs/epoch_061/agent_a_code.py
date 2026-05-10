def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    # Corner running hint for evader
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if pursuer:
        targetx, targety = ox, oy
    else:
        # Prefer farthest corner from pursuer, but still react to exact pursuer position
        c = max(corners, key=lambda p: (abs(p[0] - ox) + abs(p[1] - oy), p[0], p[1]))
        targetx, targety = c[0], c[1]

    best = None
    if pursuer:
        # minimize distance to opponent; tie-break by higher mobility and then lexicographic move
        best_val = 10**18
        best_m = -10**18
        best_lex = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            m = mobility(nx, ny)
            # small bias to move toward targetx/targety to prevent stalling
            bias = 0.01 * cheb(nx, ny, targetx, targety)
            val = (d, bias)
            if val[0] < best_val or (val[0] == best_val and (m > best_m or (m == best_m and (best_lex is None or (dx, dy) < best_lex)))):
                best_val = val[0]
                best_m = m
                best_lex = (dx, dy)
                best = [dx, dy]
    else:
        # maximize distance from pursuer; tie-break by higher mobility and then lexicographic move
        best_val = -10**18
        best_m = -10**18
        best_lex = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            m = mobility(nx, ny)
            bias = 0.01 * cheb(nx, ny, targetx, targety)
            val = (d, -bias)
            if val[0] > best_val or (val[0] == best_val and (m > best_m or (m == best_m and (best_lex is None or (dx, dy) < best_lex)))):
                best_val = val[0]
                best_m = m
                best_lex = (dx, dy)
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]