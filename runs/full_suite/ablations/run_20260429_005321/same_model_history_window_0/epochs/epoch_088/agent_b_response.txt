def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_val = -10**9

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, drift toward center while avoiding obstacles
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h: 
                continue
            if (nx, ny) in obs:
                continue
            val = -cheb((nx, ny), (cx, cy))
            if val > best_val:
                best_val = val
                best = [dx, dy]
        return best if best is not None else [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        me = (nx, ny)
        # Evaluate best resource we could contest
        local_best = -10**9
        for rx, ry in resources:
            r = (rx, ry)
            d_me = cheb(me, r)
            d_opp = cheb((ox, oy), r)
            # Prefer positions that make us strictly closer; reward very close pickups
            adv = d_opp - d_me
            val = adv * 10 - d_me
            if d_me == 0:
                val += 1000
            if val > local_best:
                local_best = val
        # Slight bias to keep moves stable: prefer smaller Chebyshev step when equal
        step_bias = 0 if (dx == 0 and dy == 0) else -1
        total = local_best + step_bias
        if total > best_val:
            best_val = total
            best = [dx, dy]

    return best if best is not None else [0, 0]