def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((a, b) for a, b in obs)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_val = -10**18

    if not resources:
        # deterministic: try to move closer to opponent by manhattan
        order = sorted(moves, key=lambda m: abs((sx+m[0])-ox) + abs((sy+m[1])-oy))
        for dx, dy in order:
            nx, ny = sx+dx, sy+dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        val = - (abs(nx - ox) + abs(ny - oy))  # basic pressure to reduce opponent distance
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            # prioritize getting where we beat the opponent; slight preference for closer points
            val += (2000 if ds < do else (0 if ds == do else -5)) - ds
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]