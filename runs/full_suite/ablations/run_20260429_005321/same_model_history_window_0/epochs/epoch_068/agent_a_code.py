def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]
    if not resources:
        deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dO = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
                if (-dO, nx, ny) < (best[0], best[1], best[2]):
                    best = (-dO, nx, ny)
        return [best[1] - sx, best[2] - sy]

    # Pick target resource
    best_val = -10**18
    target = resources[0]
    for rx, ry in resources:
        dS = abs(rx - sx) + abs(ry - sy)
        dO = abs(rx - ox) + abs(ry - oy)
        val = dO - dS  # positive: we are closer
        if val > best_val or (val == best_val and (dS < (abs(target[0] - sx) + abs(target[1] - sy)))):
            best_val = val
            target = (rx, ry)

    contest = best_val <= 0  # opponent is closer or equal to the best we found

    tx, ty = target
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_score = -10**18
    best_dx = 0
    best_dy = 0
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        distT = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        distO = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Always minimize distT; if contesting, slightly prefer moves that also reduce distO (intercept)
        score = -distT + (0.05 * distO if not contest else -0.05 * distO)
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]