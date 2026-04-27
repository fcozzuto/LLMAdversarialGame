def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)
    candidates = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy
    if resources:
        curr_best = min(dist2(sx, sy, r[0], r[1]) for r in resources)
    else:
        curr_best = 10**9
    best = None
    best_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        if resources:
            new_best = min(dist2(nx, ny, r[0], r[1]) for r in resources)
            on_res = any((nx, ny) == (r[0], r[1]) for r in resources)
        else:
            new_best = 10**9
            on_res = False
        opp_d2 = dist2(nx, ny, ox, oy)
        # Key: maximize improvement; then maximize distance from opponent; then deterministic move choice
        improve = curr_best - new_best
        bonus = 10**6 if on_res else 0
        key = (bonus + improve, opp_d2, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best