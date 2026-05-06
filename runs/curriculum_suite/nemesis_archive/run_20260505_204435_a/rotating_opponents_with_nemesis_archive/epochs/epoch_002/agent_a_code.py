def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    (sx, sy) = observation["self_position"]; (ox, oy) = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    def dist2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx * dx + dy * dy

    if resources:
        best = None
        for rx, ry in resources:
            sd = dist2(sx, sy, rx, ry)
            od = dist2(ox, oy, rx, ry)
            key = (-(od - sd), sd, od, rx, ry)  # smaller is better
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    best_m = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            e_self = dist2(nx, ny, tx, ty)
            e_opp = dist2(ox, oy, tx, ty)
            key = (e_self - e_opp, e_self, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best_m is None or key < best_m[0]:
                best_m = (key, dx, dy)

    if best_m is not None:
        return [best_m[1], best_m[2]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            e_self = dist2(nx, ny, tx, ty)
            e_opp = dist2(ox, oy, tx, ty)
            key = (e_self - e_opp, e_self, dx, dy)
            if best_m is None or key < best_m[0]:
                best_m = (key, dx, dy)
    return [best_m[1], best_m[2]]