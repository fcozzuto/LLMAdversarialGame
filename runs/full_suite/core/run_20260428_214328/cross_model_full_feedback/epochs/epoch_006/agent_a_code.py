def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): 
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy
    # valid single-step moves (engine rejects invalid by staying, so filter)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != (ox, oy)
    # Determine which resources we can "race" for
    best_r = None; best_gap = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        gap = do - ds  # positive means we are closer
        # prefer resources that are likely ours (positive gap), and earlier by ds
        score = gap * 100 - ds
        if score > best_gap:
            best_gap = score
            best_r = (rx, ry, gap, ds, do)
    # If we aren't ahead for any resource, disrupt: head toward corner opposite opponent or maximize distance
    if best_r is None or best_r[2] <= 0:
        target = (0, 0) if (ox + oy) > (w - 1 + h - 1 - (ox + oy)) else (w - 1, h - 1)
        tx, ty = target
        # also avoid stepping into opponent reach: prefer steps increasing dist to opponent
        best_m = [0, 0]; best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            val = man(nx, ny, ox, oy) * 10 - man(nx, ny, tx, ty)
            if val > best_val:
                best_val = val; best_m = [dx, dy]
        return best_m
    # We are ahead: move greedily toward the best raced resource with obstacle-aware tie-breaking
    rx, ry = best_r[0], best_r[1]
    # choose move that reduces ds most; tie-break by staying away from opponent
    best_m = [0, 0]; best_ds = 10**9; best_sep = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = man(nx, ny, rx, ry)
        sep2 = man(nx, ny, ox, oy)
        if ds2 < best_ds or (ds2 == best_ds and sep2 > best_sep):
            best_ds = ds2; best_sep = sep2; best_m = [dx, dy]
    return best_m