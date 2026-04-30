def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]
    deltas = [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Choose a resource where we are relatively closer than the opponent.
    if resources:
        best = None
        best_gap = None
        best_dist = None
        for r in resources:
            ds = man((sx,sy), r)
            do = man((ox,oy), r)
            gap = do - ds
            if best is None or gap > best_gap or (gap == best_gap and (ds < best_dist)):
                best, best_gap, best_dist = r, gap, ds
        target = best
    else:
        target = (sx, sy)

    # If we're not currently advantaged for any target, fall back to nearest resource.
    if resources:
        nearest = min(resources, key=lambda r: man((sx,sy), r))
        ds_near = man((sx,sy), nearest)
        do_near = man((ox,oy), nearest)
        if do_near - ds_near < 0:
            target = nearest

    # Score candidate moves.
    best_move = (0,0)
    best_tuple = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = man((nx, ny), target)
        d_o = man((nx, ny), (ox, oy))

        # If opponent is too close, bias to increase separation.
        close = 2 if (man((sx,sy), (ox,oy)) <= 2) else 0
        # Tuple: minimize distance to target, maximize distance to opponent (via negative), tie-break deterministically.
        cand_tuple = (d_t, -(d_o + close), dx, dy)
        if best_tuple is None or cand_tuple < best_tuple:
            best_tuple = cand_tuple
            best_move = [dx, dy]

    return best_move