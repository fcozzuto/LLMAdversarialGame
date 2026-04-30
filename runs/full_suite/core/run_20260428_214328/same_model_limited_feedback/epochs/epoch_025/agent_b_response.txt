def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev for 8-way

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_move_towards(tx, ty):
        best = None
        best_val = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            d_here = dist((nx, ny), (tx, ty))
            d_opp = dist((nx, ny), (ox, oy))
            # Primary: get closer to target; Secondary: increase separation from opponent; Tertiary: deterministic preference
            val = (-d_here * 10) + (d_opp * 1)
            # Tie-break: prefer keeping dx earlier in deltas order via small bias
            if best is None or val > best_val:
                best_val = val
                best = (dx, dy)
        return best if best is not None else (0, 0)

    if resources:
        # Choose resource that is "most available" for us vs opponent
        best_r = None
        best_s = 10**18
        for rx, ry in resources:
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # Prefer resources closer to us; discourage those much closer to opponent
            s = sd - (od * 0.6)
            if s < best_s:
                best_s = s
                best_r = (rx, ry)
            elif s == best_s and (sd < dist((sx, sy), best_r)):
                best_r = (rx, ry)
        tx, ty = best_r
        return list(best_move_towards(tx, ty))

    # If no resources remain: drift toward center while avoiding obstacles and keeping away from opponent
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dc = max(abs(nx - cx), abs(ny - cy))
        d_opp = dist((nx, ny), (ox, oy))
        val = (-dc * 10) + d_opp
        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]