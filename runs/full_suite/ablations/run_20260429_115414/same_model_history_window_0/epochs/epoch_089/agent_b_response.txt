def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    # Pick a target resource where we are comparatively closer than opponent
    best = None
    best_key = None
    for rx, ry in resources:
        ds = (sx-rx)*(sx-rx) + (sy-ry)*(sy-ry)
        do = (ox-rx)*(ox-rx) + (oy-ry)*(oy-ry)
        # prefer: we are closer (higher gap), and overall reasonable distance
        key = ((do - ds), -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key; best = (rx, ry)
    if best is None:
        # No resources: head toward opponent to contest space
        tx, ty = ox, oy
    else:
        tx, ty = best

    # Consider moves that don't hit obstacles or go out of bounds
    best_move = (0, 0); best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        dist = (nx-tx)*(nx-tx) + (ny-ty)*(ny-ty)
        # Light obstacle avoidance: penalize stepping adjacent to obstacles
        adj_pen = 0
        for adx, ady in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            ax, ay = nx+adx, ny+ady
            if inb(ax, ay) and (ax, ay) in obstacles:
                adj_pen += 2
        # Tie-break deterministically: prefer moves that reduce x then y movement toward target
        toward = (1 if nx > tx else -1 if nx < tx else 0) * dx + (1 if ny > ty else -1 if ny < ty else 0) * dy
        score = (dist + adj_pen*1.0, -toward, abs(dx)+abs(dy))
        if best_score is None or score < best_score:
            best_score = score; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]