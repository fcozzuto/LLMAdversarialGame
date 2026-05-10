def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list if p is not None and len(p) >= 2}

    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = None
    best_move = (0, 0)

    # Evaluate moves by "who would arrive first" to the same resource after one step.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Best resource for this move: minimize (self_after - opp_now), then minimize self_after, then resource coords.
        move_best = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if not ok(rx, ry):
                continue
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            val = (d_self - d_opp, d_self, rx, ry)
            if move_best is None or val < move_best:
                move_best = val

        if move_best is None:
            continue

        # Prefer actions that improve first-arrival margin; break ties deterministically by (dx,dy) and position.
        # Here: maximize margin == minimize (d_self - d_opp), same as move_best[0]; include small term for staying efficient.
        final_val = (move_best[0], move_best[1], ny, nx, dy, dx)
        if best is None or final_val < best:
            best = final_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]