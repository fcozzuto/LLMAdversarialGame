def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)
    role = (observation.get("self_role") or "").lower()
    is_pursuer = "pursuer" in role

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for ddx, ddy in deltas:
            nx, ny = x + ddx, y + ddy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    def obstacle_near_penalty(x, y):
        # small penalty for being close to obstacles (encourage safer corridors)
        best = 10**9
        for ax, ay in obstacles:
            dx, dy = x - ax, y - ay
            d = dx * dx + dy * dy
            if d < best:
                best = d
        if best == 10**9:
            return 0
        if best <= 1:
            return 50
        if best <= 4:
            return 15
        if best <= 9:
            return 6
        return 0

    best = None
    best_val = None  # compare based on is_pursuer
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        d = dist2(nx, ny)
        mob = mobility(nx, ny)
        pen = obstacle_near_penalty(nx, ny)
        if is_pursuer:
            # primary: minimize distance; secondary: prefer higher mobility; tertiary: avoid obstacles
            val = (d * 1000) - (mob * 10) + pen
            better = best_val is None or val < best_val
        else:
            # primary: maximize distance; secondary: prefer higher mobility; tertiary: avoid obstacles
            val = (-d * 1000) + (mob * 10) + pen
            better = best_val is None or val > best_val
        if better:
            best_val = val
            best = (ddx, ddy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]