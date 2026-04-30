def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    w, h = observation["grid_width"], observation["grid_height"]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_delta = (0, 0)
    best_val = -10**9

    def eval_pos(nx, ny):
        # If stepping into obstacle or out of bounds, heavily penalize
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return -10**9
        if (nx, ny) in obstacles:
            return -10**9

        # Separation pressure: small, to avoid being run over
        sep = dist((nx, ny), (ox, oy))
        sep_bonus = sep * 0.15

        if not resources:
            # Go toward center deterministically
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dc = abs(nx - cx) + abs(ny - cy)
            return sep_bonus - dc * 0.01

        # Target resource where our lead (opponent farther) is greatest
        # Prefer getting closer to that resource when tied
        best = -10**9
        for rx, ry in resources:
            d_self = dist((nx, ny), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # Winning contest metric: maximize (opp distance - self distance)
            lead = d_opp - d_self
            tie = -d_self * 0.05
            # Slight preference to resources closer to the center (more likely contested)
            center = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
            center_pref = -center * 0.002
            val = lead * 1.0 + tie + center_pref
            if val > best:
                best = val
        return best + sep_bonus

    # Deterministic tie-break order already in deltas list
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        v = eval_pos(nx, ny)
        if v > best_val:
            best_val = v
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]