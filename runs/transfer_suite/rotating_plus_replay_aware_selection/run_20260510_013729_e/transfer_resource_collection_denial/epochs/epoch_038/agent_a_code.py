def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    # New policy: for each candidate move, pick the resource where we gain most over opponent
    # after the move; if we're never ahead, go to reduce our deficit the most.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        local_best = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gain = do - ds  # positive = we are closer (better)
            # Tie-break: prefer smaller ds to get the pickup sooner, then consistent ordering.
            key = (gain, -ds, -(rx * 8 + ry))
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue

        # For resources where we're ahead, maximize gain strongly; otherwise maximize (-deficit) by gain itself.
        overall_key = local_best
        if best is None or overall_key > best:
            best = overall_key
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]