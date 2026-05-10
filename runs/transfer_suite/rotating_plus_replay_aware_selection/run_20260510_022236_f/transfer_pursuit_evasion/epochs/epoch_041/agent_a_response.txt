def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp_move(nx, ny):
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        return nx, ny

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    def obstacle_risk(x, y):
        if (x, y) in obs:
            return 10**9
        # small deterrent for proximity
        risk = 0
        for (ox2, oy2) in obs:
            d = abs(x - ox2) + abs(y - oy2)
            if d == 0:
                return 10**9
            if d == 1:
                risk += 5
            elif d == 2:
                risk += 2
        return risk

    best = None
    best_m = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp_move(nx, ny)
        risk = obstacle_risk(nx, ny)
        if risk >= 10**8:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        # Heuristic: cut off (pursuer) / flee from direct pursuit (evader) while avoiding edges/obstacles.
        wd = wall_dist(nx, ny)
        if is_evader:
            score = dist * 2 + wd * 0.7 - risk * 3
        else:
            # also prefer moves that reduce both x and y gap when possible
            score = -dist * 2 + wd * 0.2 - risk * 3 - 0.01 * (abs((nx - ox)) + abs((ny - oy)))
        if best is None or score > best:
            best = score
            best_m = (dx if (sx + dx) >= 0 and (sx + dx) < w else 0,
                      dy if (sy + dy) >= 0 and (sy + dy) < h else 0)
    dx, dy = best_m
    return [int(dx), int(dy)]