def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # Candidate moves
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**9
    # Precompute some quick stats
    if not resources:
        # Move away from opponent deterministically
        dx = -1 if ox > sx else (1 if ox < sx else 0)
        dy = -1 if oy > sy else (1 if oy < sy else 0)
        return [dx, dy]
    # Target evaluation depends on who is closer to resources; avoid getting "lured"
    # Also add a small bias to resources that are closer to the center (to spread).
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    # Heuristic: for each move, maximize (opp_closer_distance - self_distance) to prioritize resources we can grab first.
    # If that is tied/weak, prefer moves that also reduce our distance to the closest resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Compute value by considering the best resource after move
        v = -dist((nx, ny), (ox, oy)) * 0.02  # slight distancing from opponent
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_s = dist((nx, ny), (rx, ry))
            d_o = dist((ox, oy), (rx, ry))
            # Positive means we are closer than opponent
            advantage = (d_o - d_s)
            center_bias = -0.001 * (abs(rx - cx) + abs(ry - cy))
            # Penalize moving onto a resource only if opponent is about to take it much sooner
            urgency = 0
            if d_s == 0:
                urgency = 1000
            elif d_o - d_s >= 2:
                urgency = 40
            elif d_o - d_s >= 0:
                urgency = 10
            v = max(v, advantage * 2.5 + center_bias + urgency)
        # Add obstacle adjacency penalty to discourage walking into tight areas
        adj_pen = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obstacles:
                adj_pen -= 2
        v += adj_pen
        # Tie-break deterministically: prefer moves with smaller dx, then smaller dy, then lexicographically.
        if best is None or v > best_val or (v == best_val and (dx, dy) < best):
            best_val = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]