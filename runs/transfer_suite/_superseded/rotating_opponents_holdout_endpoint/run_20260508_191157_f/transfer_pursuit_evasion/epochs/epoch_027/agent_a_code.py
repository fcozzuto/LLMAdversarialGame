def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("flee" in role) or ("escape" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        if (nx, ny) in obs:
            return None
        return nx, ny

    def cheb_dist(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    def man_dist_to_obstacles(x, y):
        if not obstacles:
            return 10**6
        best = 10**6
        for px, py in obstacles:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_val = None  # higher is better in both cases; sign chosen by strategy

    for dx, dy in dirs:
        nxt = clamp_move(dx, dy)
        if nxt is None:
            continue
        nx, ny = nxt
        d = cheb_dist(nx, ny)
        dob = man_dist_to_obstacles(nx, ny)

        # Prefer staying farther from obstacles; weight stronger for evader.
        obstacle_term = dob
        if dob <= 1:
            obstacle_term -= 10  # strong repulsion near obstacles

        if is_evader:
            # Maximize separation; add slight preference for moving toward the farthest corner
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_term = - (abs(nx - far_corner[0]) + abs(ny - far_corner[1]))  # closer to far corner is higher
            val = d * 10 + obstacle_term * 2 + corner_term
        else:
            # Minimize separation; add obstacle avoidance
            val = -d * 10 + obstacle_term * 2

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]