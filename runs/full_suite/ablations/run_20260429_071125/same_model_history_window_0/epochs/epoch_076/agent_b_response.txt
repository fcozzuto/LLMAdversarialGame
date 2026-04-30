def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def d2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy

    # Select a target resource where we're relatively closer than opponent
    if resources:
        best = None
        best_gap = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = (rx - sx)*(rx - sx) + (ry - sy)*(ry - sy)
            od = (rx - ox)*(rx - ox) + (ry - oy)*(ry - oy)
            gap = od - sd  # larger means we are closer
            key = (gap, -sd)
            if best is None or key > best_gap:
                best = (rx, ry)
                best_gap = key
        tx, ty = best if best is not None else (w//2, h//2)
    else:
        tx, ty = w//2, h//2

    # Move one step to reduce distance to target; avoid obstacles
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        val = -d2(nx, ny, tx, ty)  # maximize negative distance
        # slight bias: if opponent is also near the target, prefer moves that increase separation
        val += 0.01 * d2(nx, ny, ox, oy)
        # if stepping onto a resource, strongly prioritize
        if (nx, ny) in set(tuple(p) for p in resources):
            val += 1e6
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]