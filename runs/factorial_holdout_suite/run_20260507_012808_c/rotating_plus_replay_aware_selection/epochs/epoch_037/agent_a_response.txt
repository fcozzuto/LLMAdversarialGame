def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        nx, ny = sx, sy
        tx, ty = 0, 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    rset = set((r[0], r[1]) for r in resources)
    opp_best_d = min(king_dist(ox, oy, rx, ry) for rx, ry in resources)
    opp_best_targets = [r for r in resources if king_dist(ox, oy, r[0], r[1]) == opp_best_d]
    opp_threat = min(opp_best_targets, key=lambda r: king_dist(sx, sy, r[0], r[1]))
    tx0, ty0 = opp_threat

    best_move = (0, 0)
    best_val = -10**18

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        immediate = 0
        if (nx, ny) in rset:
            immediate = 10**6

        # Choose best target from our perspective for this move (still deterministic).
        best_target = None
        best_priority = -10**18
        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            opd = king_dist(ox, oy, rx, ry)
            # Higher when we are closer than opponent, and when target is nearer overall.
            priority = (opd - myd) * 500 - myd + (1 if (rx, ry) == (tx0, ty0) else 0) * 200
            if priority > best_priority:
                best_priority, best_target = priority, (rx, ry)
            elif priority == best_priority and (rx, ry) < best_target:
                best_target = (rx, ry)

        rx, ry = best_target
        myd = king_dist(nx, ny, rx, ry)
        opd = king_dist(ox, oy, rx, ry)
        # If we can secure sooner than opponent, strongly favor it.
        winish = 3000 if myd < opd else (1000 if myd == opd else 0)
        # Slightly bias toward reducing opponent's closest-to-them target pressure.
        opp_dist_to_move = king_dist(ox, oy, nx, ny)
        val = immediate + best_priority + winish + (opp_best_d - opp_dist_to_move) * 5

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]