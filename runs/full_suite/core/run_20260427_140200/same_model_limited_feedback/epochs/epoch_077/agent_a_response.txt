def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    candidates = []
    for dx in dxs:
        for dy in dys:
            candidates.append((dx, dy))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def best_value(newpos):
        if not resources:
            return -dist2(newpos, (ox, oy))
        my_best = None
        my_dist = 10**18
        for r in resources:
            d = dist2(newpos, r)
            if d < my_dist:
                my_dist = d
                my_best = r
        r = my_best
        opp_d = dist2((ox, oy), r)
        if my_dist == 0:
            return 10**9  # immediate pickup
        # Prefer reducing my distance to a resource, and contesting resources the opponent is closer to
        return (opp_d - my_dist) * 3 - my_dist + dist2(newpos, (ox, oy)) * (-0.05)

    best = None
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            nx, ny = sx, sy
        val = best_value((nx, ny))
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]