def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = [0, 0]
        bestd = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if bestd is None or d < bestd:
                bestd = d
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Prefer moves that increase our distance advantage to the most "valuable" contested resource.
        local_best = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            advantage = do - ds  # positive means we are closer after the move
            # Tie-break: prefer closer ds, then prefer resources that are currently closer to the opponent (more contested).
            key = (advantage, -ds, do)
            if local_best is None or key > local_best:
                local_best = key
        # Global tie-break: prefer larger advantage, then smaller self distance to best target, then deterministic direction order.
        if local_best is None:
            continue
        if best_key is None or local_best > best_key:
            best_key = local_best
            best_move = [dx, dy]

    return best_move