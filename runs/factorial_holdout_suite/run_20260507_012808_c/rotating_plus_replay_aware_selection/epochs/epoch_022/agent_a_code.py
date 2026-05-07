def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resset = set((r[0], r[1]) for r in resources)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # Evaluate each candidate move by best immediate "lead" over opponent at a resource.
    best_val = None
    best_move = (0, 0)

    cur_center = cheb(sx, sy, cx, cy)
    cur_opp_lead = 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # If we can collect immediately, prioritize heavily.
        immediate = 1 if (nx, ny) in resset else 0

        # Choose target resource where (opp_time - self_time) is maximized.
        lead_best = -10**9
        dist_to_target_best = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            if lead > lead_best or (lead == lead_best and ds < dist_to_target_best):
                lead_best = lead
                dist_to_target_best = ds

        center_pen = 0.1 * cheb(nx, ny, cx, cy)
        away_pen = 0.05 * max(0, cheb(nx, ny, sx, sy) - 0)  # tiny, deterministic

        val = immediate * 1000 + lead_best * 10 - center_pen - away_pen
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    # If still poor (e.g., no resources), drift to center away from opponent direction.
    if not resources:
        best_val = None
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            val = (cheb(ox, oy, nx, ny) - cheb(ox, oy, sx, sy)) - 0.2 * cheb(nx, ny, cx, cy)
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]