def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set(obstacles_list)

    def dist(x1, y1, x2, y2):
        a = x1 - x2
        b = y1 - y2
        a = a if a >= 0 else -a
        b = b if b >= 0 else -b
        return a if a > b else b

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    tx = ty = None
    best = None
    if resources:
        mx = (w - 1) // 2
        my = (h - 1) // 2
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            if ds == 0:
                tx, ty = rx, ry
                break
            # Prefer resources we can reach no slower than opponent; then nearer; then closer to center.
            reach_bias = ds - do
            center_bias = abs(rx - mx) + abs(ry - my)
            cand = (0 if reach_bias <= 0 else 1, reach_bias, ds, center_bias)
            if best is None or cand < best:
                best = cand
                tx, ty = rx, ry

    if tx is None:
        # No resources: move to maximize distance from opponent
        best_score = None
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            score = dist(nx, ny, ox, oy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # With a target: minimize our distance; if tied, maximize opponent distance from target
    best_score = None
    best_move = (0, 0)
    tdx, tdy = tx, ty
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        ds = dist(nx, ny, tdx, tdy)
        do = dist(ox, oy, tdx, tdy)
        score = (ds, -do, abs(nx - tdx) + abs(ny - tdy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]