def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        best = (10**9, 0, 0)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = max(abs(nx - ox), abs(ny - oy))
                key = (d, dx, dy)
                if key < best:
                    best = key
        return [best[1], best[2]]

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    # Choose target resource deterministically by "winning margin" against opponent.
    tx, ty = resources[0]
    best_metric = None
    best_t = (tx, ty)
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        metric = (my_d - op_d, my_d, rx, ry)  # smaller is better
        if best_metric is None or metric < best_metric:
            best_metric = metric
            best_t = (rx, ry)
    tx, ty = best_t

    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_key = None
    best_move = (0, 0)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        my_d2 = cheb(nx, ny, tx, ty)
        # Recompute opponent's ability to also reach target next step (approx).
        op_candidates = [(k, l) for k in (-1, 0, 1) for l in (-1, 0, 1)]
        op_best = 10**9
        for k, l in op_candidates:
            px, py = ox + k, oy + l
            if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
                d = cheb(px, py, tx, ty)
                if d < op_best:
                    op_best = d
        # Prefer reducing distance to target; also prefer making opponent farther.
        key = (my_d2 - op_best, my_d2, cheb(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]