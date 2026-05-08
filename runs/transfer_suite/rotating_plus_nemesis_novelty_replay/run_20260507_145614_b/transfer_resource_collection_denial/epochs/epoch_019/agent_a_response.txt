def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def target_score(rx, ry):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if do < ds:
            return 10**6 + (ds - do)  # discourage targets opponent can reach first
        return (ds * 2) + (do - ds)

    best_r = None
    best_s = 10**18
    for rx, ry in resources:
        if valid(rx, ry):
            s = target_score(rx, ry)
            if s < best_s or (s == best_s and (best_r is None or (rx, ry) < best_r)):
                best_s = s
                best_r = (rx, ry)

    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds1 = cheb(nx, ny, tx, ty)
        if best_r is None:
            do1 = cheb(ox, oy, tx, ty)
            val = ds1 * 2 + (do1 - ds1)
        else:
            # Prefer reducing distance to the chosen target; small tie-break by opponent distance to that same target.
            do1 = cheb(ox, oy, tx, ty)
            if do1 < ds1:
                val = 10**6 + (ds1 - do1)
            else:
                val = ds1 * 2 + (do1 - ds1)
        # Deterministic tie-break: prefer lower dx/dy lexicographically after val.
        if val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]