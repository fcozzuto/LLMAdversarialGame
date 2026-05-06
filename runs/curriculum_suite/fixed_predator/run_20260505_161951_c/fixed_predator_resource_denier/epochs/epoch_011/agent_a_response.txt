def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def cheb(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da if da > db else db

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            v = -cheb(nx, ny, cx, cy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # One-step deterministic scoring: maximize how much closer we are than opponent to some resource.
    best_move = [0, 0]
    best_score = -10**18
    best_tiebreak = 10**9
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        # Choose the best resource for us under this move.
        local_best = -10**18
        local_sd = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            v = od - sd  # positive if we are closer than opponent to that resource
            if v > local_best or (v == local_best and sd < local_sd):
                local_best = v
                local_sd = sd

        # Encourage staying on a nearer resource and reducing our distance.
        score = local_best * 1000 - local_sd
        # Deterministic tie-break: prefer moves with smaller |dx|+|dy|, then dx,dy.
        dist_step = abs(dx) + abs(dy)
        tb = (dist_step, dx, dy, local_sd)
        best_tb = (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1], best_tiebreak)

        if score > best_score or (score == best_score and tb < best_tb):
            best_score = score
            best_move = [dx, dy]
            best_tiebreak = local_sd

    return best_move