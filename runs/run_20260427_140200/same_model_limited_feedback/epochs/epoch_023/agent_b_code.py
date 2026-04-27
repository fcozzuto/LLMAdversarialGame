def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    # Determine candidates
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Helper
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy
    # If no resources, head to center and away from opponent
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            v = dist2((nx, ny), (cx, cy)) - 0.3 * dist2((nx, ny), (ox, oy))
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))
    # Strategic evaluation: pick a move that improves our access to resources that are comparatively worse for opponent
    best = (0, 0)
    bestv = None
    res_list = [tuple(r) for r in resources if tuple(r) not in obstacles]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # Immediate benefit if landing on a resource
        immediate = 0.0
        if (nx, ny) in set(res_list):
            immediate += -5.0
        # Choose resource that minimizes (our distance - advantage weight * opponent distance)
        # Larger opponent proximity should reduce our desirability.
        my_best = None
        for rx, ry in res_list:
            d_my = dist2((nx, ny), (rx, ry))
            d_op = dist2((ox, oy), (rx, ry))
            v = d_my - 0.85 * d_op
            if my_best is None or v < my_best:
                my_best = v
        # Also encourage not being trapped by opponent: if we are too close, slightly pull away
        close_pen = 0.0
        dpo = dist2((nx, ny), (ox, oy))
        if dpo < 9:  # within 3 steps (chebyshev-ish via squared)
            close_pen = (9 - dpo) * 0.08
        # Mild preference to reduce distance to opponent-occupied direction if contesting
        v_move = immediate + (my_best if my_best is not None else 0.0) + close_pen
        if bestv is None or v_move < bestv:
            bestv = v_move
            best = (dx, dy)
    return [int(best[0]), int(best[1])]