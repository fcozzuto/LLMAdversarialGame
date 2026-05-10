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

    def score_move(nx, ny):
        d = cheb(nx, ny, ox, oy)
        m = mobility(nx, ny)
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center = -cheb(nx, ny, cx, cy)  # closer to center -> less negative
        if pursuer:
            # minimize distance; prefer higher mobility and center a bit when tied
            return (-d, -(-m), -center)
        else:
            # maximize distance; prefer higher mobility and avoid getting trapped near borders/obstacles
            return (d, m, center)

    best = None
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = score_move(nx, ny)
        if best_s is None:
            best_s, best = s, (dx, dy)
        else:
            if pursuer:
                if s < best_s:
                    best_s, best = s, (dx, dy)
            else:
                if s > best_s:
                    best_s, best = s, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]