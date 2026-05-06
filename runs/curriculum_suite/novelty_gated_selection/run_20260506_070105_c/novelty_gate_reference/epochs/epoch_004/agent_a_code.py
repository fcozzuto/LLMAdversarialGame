def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    blocked = set((p[0], p[1]) for p in obstacles)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Choose a target resource: prioritize being closer than opponent; then being close; then center.
    tx = ty = None
    if resources:
        cx = (w - 1) / 2.0; cy = (h - 1) / 2.0
        best_key = None
        for rx, ry in resources:
            du = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            lead = do - du  # >0 means we are closer
            center_dist = abs(rx - cx) + abs(ry - cy)
            # Prefer higher lead, then smaller du, then more central
            key = (-lead, du, center_dist, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                tx, ty = rx, ry
    if tx is None:
        tx, ty = ox, oy

    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(nx - ox) + abs(ny - oy)
        # Make progress to target while not allowing opponent to get closer (prefer higher opp_d).
        center_bias = abs((nx - (w - 1) / 2.0)) + abs((ny - (h - 1) / 2.0))
        key = (my_d, -opp_d, center_bias, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]