def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    # Choose resource where we are relatively closer than opponent (minimize myd-od).
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (myd - od, myd, od)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Greedy one-step move toward target, avoiding stepping into obstacles/bounds.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        # Also discourage moves that let opponent get relatively closer to the same target.
        od = cheb(ox, oy, tx, ty)
        val = (myd, myd - od, abs((nx - tx)) + abs((ny - ty)))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]