def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = {(x, y) for x, y in obstacles}

    best_dxdy = [0, 0]
    best_score = -10**18

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If no resources, drift toward opponent to prevent free movement
    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        # Choose the resource where we are relatively closer than the opponent
        best_diff = -10**18
        best_self_d = 10**18
        for r in resources:
            if tuple(r) in obs_set:
                continue
            sd = dist2((nx, ny), r)
            od = dist2((ox, oy), r)
            diff = od - sd  # positive means we are closer
            if diff > best_diff or (diff == best_diff and sd < best_self_d):
                best_diff = diff
                best_self_d = sd

        # Add small tie-breakers: prefer closer absolute resource and moving slightly toward center
        center_bias = -dist2((nx, ny), (w // 2, h // 2)) * 1e-4
        score = best_diff - best_self_d * 1e-3 + center_bias

        if score > best_score:
            best_score = score
            best_dxdy = [dx, dy]

    return best_dxdy