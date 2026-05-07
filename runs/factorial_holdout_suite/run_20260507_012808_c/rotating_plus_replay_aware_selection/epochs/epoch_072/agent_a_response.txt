def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(a, b, c, d2):
        return max(abs(c - a), abs(d2 - b))  # chebyshev

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    if not resources:
        return [0, 0]

    best_target = None
    best_key = (-10**18, 10**18, 10**18)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        self_d = d(sx, sy, rx, ry)
        # We don't know opponent start from observation schema? It exists:
        ox, oy = observation["opponent_position"]
        opp_d = d(ox, oy, rx, ry)
        win_margin = opp_d - self_d
        key = (win_margin, -self_d, rx + 7 * ry)
        if key > best_key:
            best_key = key
            best_target = (rx, ry)

    ox, oy = observation["opponent_position"]
    best_move = (0, 0)
    best_move_key = (-10**18, -10**18, 10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer moving to a resource where we have/keep a contest edge.
        local_best = (-10**18, 10**18, 10**18)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            self_d = d(nx, ny, rx, ry)
            opp_d = d(ox, oy, rx, ry)
            win_margin = opp_d - self_d
            # If ties, prefer resources closer to us; deterministic tie-break by coords sum.
            cand = (win_margin, -self_d, rx + 7 * ry)
            if cand > local_best:
                local_best = cand
        # Also discourage moves that help the opponent globally (slight): move away from opponent.
        opp_dist_after = d(nx, ny, ox, oy)
        move_key = (local_best[0], -local_best[1], -opp_dist_after)
        if move_key > best_move_key:
            best_move_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]