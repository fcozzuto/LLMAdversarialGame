def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def wall_score(x, y):
        lx = x if x < w - 1 - x else w - 1 - x
        ly = y if y < h - 1 - y else h - 1 - y
        return lx if lx < ly else ly

    def near_obstacle_penalty(x, y):
        p = 0
        for ax, ay in obstacles:
            dx = x - ax
            if dx < 0: dx = -dx
            dy = y - ay
            if dy < 0: dy = -dy
            d = dx if dx > dy else dy
            if d <= 2:
                p += (2 - d) + 1
        return p

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        obstacle_pen = near_obstacle_penalty(nx, ny)
        edge_pref = wall_score(nx, ny)
        # Small deterministic tie-breaker to avoid cycling
        tie = (dx + 1) * 9 + (dy + 1)
        if pursuer:
            val = (-(d)) * 10.0 + edge_pref * 0.6 - obstacle_pen * 3.0 - tie * 1e-3
        else:
            val = (d) * 10.0 + edge_pref * 0.3 - obstacle_pen * 3.5 - tie * 1e-3
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]