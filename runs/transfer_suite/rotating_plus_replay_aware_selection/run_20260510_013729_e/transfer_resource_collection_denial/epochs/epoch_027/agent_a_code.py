def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacle_set = {(x, y) for x, y in obstacles}

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # pick target with best "arrive earlier than opponent" advantage
    best_rx, best_ry = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, -(rx * 8 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_rx, best_ry = rx, ry
    tx, ty = best_rx, best_ry

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # evaluate moves by: keep away from obstacles, reduce distance to target, and maintain win advantage
    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        hit = (nx, ny) in obstacle_set
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # larger is better
        val = (do - ds) * 100 - ds * 3 - abs(nx - tx) - abs(ny - ty) * 0.2
        if hit:
            val -= 100000  # effectively disallow obstacle squares
        # tie-break deterministically towards smaller dx, then smaller dy
        tie = -(dx * 3 + dy)
        val2 = (val, tie)
        if best_val is None or val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]