def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)

    role = observation.get("self_role", "")
    opp_role = observation.get("opponent_role", "")

    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    pursuer = ("pursuer" in role.lower()) or ("pursuer" in opp_role.lower() and "evader" in role.lower() is False)
    best_move = [0, 0]

    if pursuer:
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
                dx, dy = 0, 0
            d = dist2(nx, ny, ox, oy)
            # Tie-break deterministically: prefer smaller dx, then smaller dy
            val = (d, abs(dx), abs(dy), dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # Evader: maximize distance, but prefer moving toward safer central-ish squares if tied.
        best_val = None
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
                dx, dy = 0, 0
            d = dist2(nx, ny, ox, oy)
            center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            # Tie-break: farther from obstacles slightly (min distance to any obstacle)
            min_obs = None
            for ex, ey in obstacles:
                md = dist2(nx, ny, ex, ey)
                if min_obs is None or md < min_obs:
                    min_obs = md
            if min_obs is None:
                min_obs = 10**9
            val = (-d, center_pen, -min_obs, dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]