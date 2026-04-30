def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
        best = None
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            v = -(abs(nx-ox)+abs(ny-oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    res_set = set((p[0], p[1]) for p in resources)
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Select target resource: prefer ones we can beat opponent for and that are close.
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # higher is better
        score = (do - ds) * 10 - ds
        # small deterministic tie-break by coordinate
        score -= (rx * 0.01 + ry * 0.001)
        if score > best_score:
            best_score = score
            best_t = (rx, ry)
    tx, ty = best_t

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        ds2 = dist(nx, ny, tx, ty)
        do2 = dist(ox, oy, tx, ty)
        d_op = dist(nx, ny, ox, oy)
        gain = 6.0 if (nx, ny) in res_set else 0.0
        avoid_op = 0.15 * d_op  # slightly prefer moving away
        v = gain + (-ds2) + 0.35 * do2 + avoid_op
        if v > bestv:
            bestv = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]