def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if (d, dx, dy) < best:
                    best = (d, dx, dy)
        return [best[1], best[2]]

    res = [tuple(r) for r in resources]
    best_val = 10**18
    best_dxdy = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer resources we can reach sooner than opponent; also prefer closer overall.
        val = 0.0
        for (rx, ry) in res:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            score = our_d - 1.15 * opp_d
            # Small bonus for being nearer to some resource (avoid overfitting to a single far one)
            score += 0.02 * our_d
            if score < val or best_dxdy == (0, 0):
                val = score
        if val < best_val or (val == best_val and (dx, dy) < best_dxdy):
            best_val = val
            best_dxdy = (dx, dy)
    return [best_dxdy[0], best_dxdy[1]]