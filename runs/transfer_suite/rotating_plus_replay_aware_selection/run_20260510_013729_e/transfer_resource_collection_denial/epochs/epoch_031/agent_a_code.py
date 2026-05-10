def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacle_set = {(x, y) for x, y in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick target: maximize arrival advantage; favor resources slightly "ahead" in the sweep direction.
    # Sweep_rows opponent tends to progress along y; bias to higher y when we are below it, else lower y.
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        ahead_bias = (ry - sy) if (ry >= sy) else -(sy - ry)
        # If opponent is closer, still allow if we can get there much faster.
        key = (do - ds, -ds, ahead_bias, -(rx * 16 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministically prefer moves that reduce our distance, maintain advantage, and avoid obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacle_set:
            continue
        ds1 = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # small preference to avoid excessive lateral drift: minimize cheb distance to target, then tie by move order
        score = (do - ds1, -ds1, -abs((nx - tx)) - abs((ny - ty)), -(dx * 3 + dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves were blocked (rare), fall back to staying.
    return [int(best_move[0]), int(best_move[1])]