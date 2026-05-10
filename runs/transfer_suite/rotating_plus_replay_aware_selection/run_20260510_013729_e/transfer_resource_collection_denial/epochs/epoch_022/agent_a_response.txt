def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacle_set = {(x, y) for x, y in obstacles}

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacle_set:
            continue

        # Local lookahead: choose neighbor that maximizes our lead to the best resource.
        # Key components: (lead) primary, then shorter self distance, then closer resource to corners (deterministic).
        max_key = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            cornerish = (rx * 8 + ry)
            key = (lead, -ds, -cornerish)
            if max_key is None or key > max_key:
                max_key = key
        # Secondary bias: prefer moves that keep options open (not surrounded by obstacles/out of bounds).
        open_neighbors = 0
        for ddx, ddy in candidates:
            ax, ay = nx + ddx, ny + ddy
            if in_bounds(ax, ay) and (ax, ay) not in obstacle_set:
                open_neighbors += 1
        move_key = (max_key[0], max_key[1], open_neighbors, max_key[2])
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]