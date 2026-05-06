def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    blocked = set((p[0], p[1]) for p in obstacles)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            du = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            contested_adv = do - du  # >0 means we are closer
            key = (-1 if contested_adv > 0 else 1, -contested_adv, du, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = ox, oy

    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = w / 2.0, h / 2.0
    best = None
    best_key = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(nx - ox) + abs(ny - oy)
        # Prefer reducing distance to target; deny opponent by increasing opp_d.
        # Tie-break toward center and then lexicographically.
        center_dist = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        key = (my_d, -(opp_d), center_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best