def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(0, 0),(1, 0),(-1, 0),(0, 1),(0, -1),(1, 1),(1, -1),(-1, 1),(-1, -1)]
    def dist(a, b):
        dx = a[0]-b[0]; dy = a[1]-b[1]
        return dx*dx + dy*dy

    best_move = (0, 0)
    best_val = None

    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        tx, ty = (w-1)//2, (h-1)//2
        for dx, dy in deltas:
            nx, ny = sx+dx, sy+dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles: 
                continue
            v = -dist((nx, ny), (tx, ty))
            if best_val is None or v > best_val:
                best_val = v; best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    opp = (ox, oy)
    for dx, dy in deltas:
        nx, ny = sx+dx, sy+dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = (nx, ny)

        # Choose a resource that maximizes how much closer we are than opponent after the move.
        local_best = None
        for r in resources:
            d_self = dist(ns, r)
            d_opp = dist(opp, r)
            # Big reward if we are closer; also prefer smaller own distance.
            v = (d_opp - d_self) * 10 - d_self
            if local_best is None or v > local_best:
                local_best = v
        if local_best is None:
            continue
        if best_val is None or local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]