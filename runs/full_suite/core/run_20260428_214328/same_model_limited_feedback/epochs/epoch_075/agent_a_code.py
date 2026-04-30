def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    # If no resources, just drift to safer corner relative to opponent
    if not resources:
        dx = -1 if sx > ox else (1 if sx < ox else 0)
        dy = -1 if sy > oy else (1 if sy < oy else 0)
        return [dx, dy]

    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): 
        dx = a[0]-b[0]; dy = a[1]-b[1]
        return (dx*dx + dy*dy)

    # Choose a target resource where we have relative advantage
    cur_self_dist = dist((sx, sy), (ox, oy))
    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Value: try to be closer than opponent; also prefer nearer overall
        val = (od - sd) * 1000 - sd
        # Mild preference toward resources closer to center to avoid corner traps
        cx = (w - 1) / 2; cy = (h - 1) / 2
        val -= (rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)
        if val > best_val:
            best_val = val; best_r = (rx, ry)

    tx, ty = best_r
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = dist((nx, ny), (tx, ty))
        cod = dist((nx, ny), (ox, oy))
        sd = dist((sx, sy), (tx, ty))
        # Encourage moving closer to target; discourage losing advantage and getting too close to opponent
        score = (sd - nsd) * 200
        score += (dist((ox, oy), (tx, ty)) - nsd) * 50
        if cod <= 2:  # too near opponent
            score -= 300
        # Obstacle proximity avoidance
        for ax, ay in obstacles:
            if dist((nx, ny), (ax, ay)) <= 1:
                score -= 150
        # If our current target is behind opponent, try to sidestep toward the "next best" fast
        if dist((sx, sy), (tx, ty)) > dist((ox, oy), (tx, ty)):
            score -= nsd // 10
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]