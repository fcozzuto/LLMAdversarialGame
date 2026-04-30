def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def clamp(x, y):
        x = 0 if x < 0 else (w-1 if x >= w else x)
        y = 0 if y < 0 else (h-1 if y >= h else y)
        return x, y

    def step_score(nx, ny, tx, ty):
        # prefer approaching target, avoid obstacles, and slightly increase separation from opponent
        if (nx, ny) in obstacles: 
            return 10**9
        d = abs(nx - tx) + abs(ny - ty)  # Manhattan is enough
        sep = abs(nx - ox) + abs(ny - oy)
        return d - 0.15 * sep

    if not resources:
        # fallback: move away from opponent to reduce interference
        tx, ty = sx, sy
    else:
        best = None
        # pick a resource to both get and deny: maximize (opp_dist - self_dist), tie-break by nearer to self
        for rx, ry in resources:
            if (rx, ry) in obstacles: 
                continue
            ds = abs(sx - rx) + abs(sy - ry)
            do = abs(ox - rx) + abs(oy - ry)
            val = (do - ds, -ds, -rx, -ry)
            if best is None or val > best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]

    # deterministic best move among legal deltas; engine will keep position if invalid
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        v = step_score(nx, ny, tx, ty)
        if best_val is None or v < best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]