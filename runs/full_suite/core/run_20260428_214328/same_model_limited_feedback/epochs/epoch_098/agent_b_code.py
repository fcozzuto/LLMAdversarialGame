def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]

    obs_set = set()
    for p in obstacles:
        obs_set.add((p[0], p[1]))

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx = cx
        ty = cy
    else:
        def dist(a, b):
            dx = a[0] - b[0]
            dy = a[1] - b[1]
            return abs(dx) + abs(dy)

        best = None
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obs_set:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            score = (do - ds, -ds)  # prefer resource closer to self than opponent
            cand = (score, rx, ry)
            if best is None or cand > best:
                best = cand
        tx, ty = best[1], best[2]

    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                moves.append((dx, dy, nx, ny))

    def dist2(nx, ny, px, py):
        return abs(nx - px) + abs(ny - py)

    if not moves:
        return [0, 0]

    best_move = None
    best_val = None
    for dx, dy, nx, ny in moves:
        d_self = dist2(nx, ny, tx, ty)
        # keep opponent pressure in mind: prefer moves that also reduce opponent advantage
        d_opp = dist2(ox, oy, tx, ty)
        val = (-(d_self), (d_opp - d_self), -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]