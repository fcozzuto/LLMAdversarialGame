def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(map(tuple, observation["obstacles"]))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    opp = (ox, oy)

    # If no resources, just drift toward center away from opponent (deterministic).
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            v = dist((nx, ny), opp) - 0.01 * (abs(nx - tx) + abs(ny - ty))
            if best is None or v > bestv:
                best, bestv = [dx, dy], v
        return best if best is not None else [0, 0]

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        self_pos = (nx, ny)
        # Evaluate the best resource for which we are currently ahead vs opponent.
        best_resource_val = -10**9
        for r in resources:
            rd = r
            sd = dist(self_pos, rd)
            od = dist(opp, rd)
            lead = od - sd  # positive means we can reach earlier (or equal)
            v = lead * 20 - sd
            if sd == 0:
                v += 1000  # prioritize immediate pickup
            # if opponent is already closer, discourage
            if lead < 0:
                v -= (-lead) * 5
            best_resource_val = max(best_resource_val, v)

        # Additional shaping: prefer moves increasing distance to opponent slightly, and avoid near-obstacle.
        opp_d = dist(self_pos, opp)
        obs_pen = 0
        for ox2, oy2 in obstacles:
            od = dist((nx, ny), (ox2, oy2))
            if od == 0:
                obs_pen += 1000
            elif od == 1:
                obs_pen += 2
        val = best_resource_val + 0.2 * opp_d - obs_pen

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move