def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    cand = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if resources:
        best = None
        best_val = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            min_d = 10**18
            for rx, ry in resources:
                dd = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if dd < min_d:
                    min_d = dd
            opp_d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            val = (min_d, -opp_d)
            if best is None or val < best_val:
                best = (dx, dy)
                best_val = val
        if best is not None:
            return [int(best[0]), int(best[1])]
    # Fallback: move to reduce distance to the center while staying away from opponent
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = (0, 0)
    best_val = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        center_d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        opp_d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val = (center_d, -opp_d)
        if best_val is None or val < best_val:
            best = (dx, dy)
            best_val = val
    return [int(best[0]), int(best[1])]