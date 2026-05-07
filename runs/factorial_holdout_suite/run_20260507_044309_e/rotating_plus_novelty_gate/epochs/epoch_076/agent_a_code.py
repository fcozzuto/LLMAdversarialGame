def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not (0 <= sx < w and 0 <= sy < h): 
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res_set = set(tuple(r) for r in resources)
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if res_set:
        for dx, dy, nx, ny in valid:
            if (nx, ny) in res_set:
                return [dx, dy]

    best = None
    best_score = None
    t = max(1, observation.get("turns_remaining", 1))
    # Deterministic target selection: prioritize resources I can secure; then closest; then edge sweep.
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        secure = do - dme  # >0 means I arrive sooner
        edge_bonus = (rx == (w - 1) or rx == 0) + 0.1 * (ry == (h - 1) or ry == 0)
        time_pressure = (t - dme) / t
        # Higher is better.
        score = (10.0 if secure > 0 else 0.0) + secure + 0.5 * time_pressure - 0.01 * dme + edge_bonus
        if best_score is None or score > best_score or (score == best_score and (rx, ry) < best):
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Choose best next step toward target while reducing risk of opponent taking it.
    best_move = [0, 0]
    best_val = None
    for dx, dy, nx, ny in valid:
        d1 = cheb(nx, ny, tx, ty)
        dme_next = d1
        do = cheb(ox, oy, tx, ty)
        # If I can still arrive no later, strongly prefer; else still prefer decreasing distance.
        secure_val = (2.0 if do - dme_next >= 0 else -2.0) + (do - dme_next)
        collect_val = 1.0 if (nx, ny) in res_set else 0.0
        wall_risk = 0.0
        if (nx, ny) in obstacles:
            wall_risk = -100.0
        # Minor deterministic tie-break: prefer moves with smaller (dx,dy) lexicographically.
        val = collect_val + secure_val - 0.05 * d1 + wall_risk
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]
    return best_move