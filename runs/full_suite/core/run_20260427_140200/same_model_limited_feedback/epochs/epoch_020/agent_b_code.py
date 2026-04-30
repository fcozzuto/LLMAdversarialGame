def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        dx = 0
        dy = 0
        best = -10**9
        for mx in (-1, 0, 1):
            for my in (-1, 0, 1):
                nx, ny = sx + mx, sy + my
                if not (0 <= nx < w and 0 <= ny < h): 
                    continue
                if (nx, ny) in obstacles:
                    continue
                val = -((nx - ox) ** 2 + (ny - oy) ** 2)
                if val > best:
                    best = val
                    dx, dy = mx, my
        return [int(dx), int(dy)]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def mindist(px, py, pts):
        bestd = 10**18
        for rx, ry in pts:
            d = (px - rx) * (px - rx) + (py - ry) * (py - ry)
            if d < bestd:
                bestd = d
        return bestd
    best_move = (0, 0)
    best_score = -10**18
    # Precompute opponent nearest distance baseline
    opp_pos = (ox, oy)
    opp_near_d = mindist(ox, oy, resources)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_near_d = mindist(nx, ny, resources)
        # Choose resource race advantage: max(opp_d - my_d)
        race = -10**18
        for rx, ry in resources:
            myd = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
            opd = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
            v = opd - myd
            if v > race:
                race = v
        # Avoid moving into opponent "range": if opponent closer than you on your nearest, discount
        nearest_resource = None
        bestd = 10**18
        for rx, ry in resources:
            d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
            if d < bestd:
                bestd = d
                nearest_resource = (rx, ry)
        block = 0
        if nearest_resource is not None:
            rx, ry = nearest_resource
            opd = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
            if opd < bestd:
                block = 5000  # deterministic penalty
        # Slight preference for progressing (smaller my_near_d) and not giving opponent improvement
        score = (race * 1000) - my_near_d - abs(my_near_d - opp_near_d) - block
        if score > best_score:
            best_score = score
            best_move = (mx, my)
    return [int(best_move[0]), int(best_move[1])]