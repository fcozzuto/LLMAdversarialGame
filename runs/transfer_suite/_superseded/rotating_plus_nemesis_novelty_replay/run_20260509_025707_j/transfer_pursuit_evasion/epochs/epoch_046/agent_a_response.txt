def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evade = ("evader" in role) or ("runner" in role) or ("evasion" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def clamp_valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # For evasion, prefer the corner farthest from opponent (deterministic).
    target_corner = corners[0]
    best_c = -10**9
    for cx, cy in corners:
        d = man(cx, cy, ox, oy)
        if d > best_c:
            best_c = d
            target_corner = (cx, cy)

    best_move = [0, 0]
    best_score = -10**18 if not evade else -10**18

    # Deterministic tie-break: fixed direction order + greater score.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not clamp_valid(nx, ny):
            continue

        d_now = man(sx, sy, ox, oy)
        d_new = man(nx, ny, ox, oy)

        # Obstacle proximity penalty (soft), strongly discourage stepping into "tight" squares.
        adj_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                if (nx + adx, ny + ady) in obstacles:
                    adj_obs += 1

        # Also gently prefer avoiding being boxed: if move puts us near many obstacles, bad.
        obstacle_pen = 3.0 * adj_obs

        if evade:
            # Maximize distance and drift toward target corner.
            tcx, tcy = target_corner
            dist_corner_now = man(sx, sy, tcx, tcy)
            dist_corner_new = man(nx, ny, tcx, tcy)
            score = (d_new * 10.0) + ((dist_corner_now - dist_corner_new) * 2.0) - obstacle_pen
        else:
            # Pursuit: minimize distance, and favor moves that reduce both axes.
            score = (-d_new * 10.0) + ((d_now - d_new) * 6.0)
            score -= obstacle_pen
            score += (-(abs(nx - ox) + abs(ny - oy)) * 0.1)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]