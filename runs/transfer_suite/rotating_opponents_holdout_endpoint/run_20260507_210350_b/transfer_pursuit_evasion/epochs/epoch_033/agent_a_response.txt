def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    evading = any(k in role for k in ("evade", "runner", "flee", "evasion", "evader"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def nearest_obst_dist(x, y):
        # small deterministic approximation: check nearby cells only
        best = 10**6
        for xx in (x-1, x, x+1):
            for yy in (y-1, y, y+1):
                if (xx, yy) in obstacles:
                    d = abs(xx-x) + abs(yy-y)
                    if d < best: best = d
        return 0 if best == 10**6 else best
    # Pursuer: minimize distance; Evader: maximize distance. Also avoid obstacles and prefer moving away from enemy when tied.
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist_cheb(nx, ny, ox, oy)
        od = nearest_obst_dist(nx, ny)
        # deterministic tie-break: (d, od, nx, ny)
        if evading:
            val = (d, od, nx, ny)
            if best_val is None or val > best_val:
                best_val, best_move = val, [dx, dy]
        else:
            val = (-d, od, -nx, -ny)
            if best_val is None or val > best_val:
                best_val, best_move = val, [dx, dy]
    if best_move is None:
        return [0, 0]
    return best_move