def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    adj_obs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def hazard(x, y):
        s = 0
        for dx, dy in adj_obs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in occ:
                s += 1
        return s

    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in occ:
                continue
            val = -man(nx, ny, cx, cy) - 0.75 * hazard(nx, ny) - 0.15 * man(nx, ny, ox, oy)
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in occ:
            continue

        center = man(nx, ny, cx, cy)
        hzl = hazard(nx, ny)

        # Interception/race: choose the resource where we are relatively closest after this move.
        best_gap = -10**18
        best_own_dist = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            gap = od - sd  # positive means we are closer than opponent
            if gap > best_gap or (gap == best_gap and sd < best_own_dist):
                best_gap = gap
                best_own_dist = sd

        # If we can't be ahead, still prefer minimizing how far behind we are.
        # Also discourage stepping into obstacle-heavy zones.
        val = 2.2 * best_gap - 0.35 * best_own_dist - 0.8 * hzl - 0.08 * center
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]