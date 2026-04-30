def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(v, a, b):
        return a if v < a else b if v > b else v

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for 8-dir grid

    cur = (sx, sy)
    opp = (ox, oy)

    # Pick resource that we can reach sooner than opponent (maximize advantage); break ties by closer to us
    best_r = None; best_key = None
    for r in resources:
        rt = (r[0], r[1])
        if rt in obstacles:
            continue
        d_ou = dist(opp, rt)
        d_su = dist(cur, rt)
        adv = d_ou - d_su  # positive means we are closer
        key = (adv, -d_su, -d_ou)
        if best_key is None or key > best_key:
            best_key = key; best_r = rt

    if best_r is None:
        best_r = resources[0] if resources else (clamp(sx,0,w-1), clamp(sy,0,h-1))

    # Score each legal move: progress to target, avoid obstacles, avoid getting too close to opponent
    tx, ty = best_r
    best_move = (0, 0); best_score = None
    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        nx = clamp(nx, 0, w-1); ny = clamp(ny, 0, h-1)
        if (nx, ny) in obstacles:
            continue
        d_to = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), opp)
        # If opponent is close, don't step onto contested squares too eagerly
        contested_pen = 0
        if resources:
            # estimate if opponent is also heading to the same target
            contested_pen = 2.0 / (1 + d_opp)
        score = (-(d_to)) + (0.15 * d_opp) - contested_pen
        # small deterministic tie-break: prefer moves with smaller dx, then dy toward target direction
        score_tuple = (score, -abs(dx), -abs(dy), dx, dy)
        if best_score is None or score_tuple > best_score:
            best_score = score_tuple; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]