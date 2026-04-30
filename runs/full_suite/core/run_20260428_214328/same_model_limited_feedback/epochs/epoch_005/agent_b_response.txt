def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def manh(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if not resources:
        # fall back: drift to center
        tx, ty = (w-1)//2, (h-1)//2
    else:
        # Pick a resource we can reach sooner than opponent (deterministic tie-break)
        best = None
        for rx, ry in resources:
            d1 = manh((sx, sy), (rx, ry))
            d2 = manh((ox, oy), (rx, ry))
            # lower is better; tie-break by our distance then by coordinates
            key = (d1 - d2, d1, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    # Choose a safe move that reduces distance to target; deterministic tie-break by lexicographic delta
    best_move = (None, None)  # (score, delta)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        # encourage moves that also prevent opponent from getting closer simultaneously
        opp_dist = abs(ox - tx) + abs(oy - ty)
        score = (dist, opp_dist - manh((ox, oy), (tx, ty)), dx, dy)
        if best_move[0] is None or score < best_move[0]:
            best_move = (score, [dx, dy])

    if best_move[1] is None:
        return [0, 0]
    return best_move[1]