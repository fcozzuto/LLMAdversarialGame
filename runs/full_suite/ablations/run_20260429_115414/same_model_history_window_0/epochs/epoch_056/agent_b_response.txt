def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def dist(a, b): 
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Pick best resource deterministically with opponent-aware scoring
    if resources:
        best = None
        best_sc = None
        for rx, ry in resources:
            if (rx, ry) in obstacles: 
                continue
            d_me = dist((sx, sy), (rx, ry))
            d_op = dist((ox, oy), (rx, ry))
            # Want to get closer than opponent; also slight central bias to reduce blocking by obstacles
            sc = (d_op - d_me) * 3.0 - d_me * 0.8 - 0.02 * (abs(rx- (w-1)/2) + abs(ry- (h-1)/2))
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources visible: move toward center while separating from opponent
        tx, ty = (w-1)/2, (h-1)/2

    # Choose move that moves toward target, avoids obstacles, and maintains distance from opponent
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        # Additional penalty if still very close to opponent (discourage collisions/contested paths)
        val = -d_to * 2.2 + d_opp * 0.9
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]