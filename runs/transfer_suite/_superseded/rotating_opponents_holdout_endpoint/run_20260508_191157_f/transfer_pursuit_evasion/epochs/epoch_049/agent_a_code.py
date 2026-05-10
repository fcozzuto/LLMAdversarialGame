def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role)
    if not (is_evader or is_pursuer):
        is_evader = False

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def cheb(x, y):
        dx = x - ox
        if dx < 0: dx = -dx
        dy = y - oy
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obstacle_count(x, y):
        c = 0
        for nx in (x - 1, x, x + 1):
            if nx < 0 or nx >= w:
                continue
            for ny in (y - 1, y, y + 1):
                if ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obs:
                    c += 1
        return c

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obs:
            score = 10**9
        else:
            d = cheb(nx, ny)
            adj = adj_obstacle_count(nx, ny)
            # Tie-breaker deterministically: prefer staying closer to center when scores equal.
            center_dist = abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny)
            if is_evader:
                score = -d + 0.35 * adj + 0.01 * center_dist
            else:
                score = d + 0.35 * adj + 0.01 * center_dist

        if best is None or (score < best_score if not is_evader else score < best_score):
            best = (dx, dy)
            best_score = score

    return [best[0], best[1]]