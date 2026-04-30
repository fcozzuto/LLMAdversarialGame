def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_from_to(tx, ty):
        dx = tx - sx
        dy = ty - sy
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx, dy

    if not resources:
        # No resources: drift toward center while avoiding obstacles
        tx, ty = w//2, h//2
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we're closer; tie-break by higher opp delay, then by coordinates
            key = (od - sd, -sd, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # Choose legal move that minimizes distance to target; tie-break by delta order.
    best_move = (0, 0)
    best_dist = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, tx, ty)
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]