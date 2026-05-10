def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("evader" in self_role)
    if ("evad" in opp_role) or ("evader" in opp_role):
        self_evader = False
    elif "purs" in self_role:
        self_evader = False

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        d = dist((nx, ny), (ox, oy))
        center_bias = -0.01 * (abs(cx - nx) + abs(cy - ny))
        boundary_pen = -0.02 * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))
        # local obstacle nudge
        near_obs = 0
        for ax, ay in obstacles:
            ax = int(ax); ay = int(ay)
            if max(abs(ax - nx), abs(ay - ny)) <= 1:
                near_obs += 1

        if self_evader:
            # maximize distance, avoid getting too close to obstacles near opponent area
            k = (d, boundary_pen + center_bias, -(near_obs))
        else:
            # minimize distance, also prefer center a bit (keeps options open around walls)
            k = (-d, center_bias + 0.5 * boundary_pen, near_obs)

        if best is None or k > best:
            best = k
            best_move = [dx, dy]

    # If everything blocked, stay put (engine will keep in place anyway)
    return best_move