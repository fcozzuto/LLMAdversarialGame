def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    if not resources:
        cx, cy = (w // 2), (h // 2)
        best = [0, 0]; best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles: 
                continue
            key = (dist((nx, ny), (cx, cy)), dx, dy)
            if best_key is None or key < best_key:
                best_key = key; best = [dx, dy]
        return best if best_key is not None else [0, 0]
    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        our_best = -10**9
        our_dist_best = 10**9
        opp_dist_best = 10**9
        for tx, ty in resources:
            od = dist((tx, ty), (ox, oy))
            nd = dist((tx, ty), (nx, ny))
            score = od - nd
            if score > our_best or (score == our_best and nd < our_dist_best):
                our_best = score
                our_dist_best = nd
                opp_dist_best = od
        # primary: maximize (opponent distance - our distance) to the best reachable resource
        # tie-breakers: smaller our distance, larger opponent distance, deterministic delta order
        key = (-our_best, our_dist_best, -opp_dist_best, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move