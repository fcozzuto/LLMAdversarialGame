def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def cheb(x1, y1, x2, y2):
        d1 = x1 - x2
        d2 = y1 - y2
        if d1 < 0: d1 = -d1
        if d2 < 0: d2 = -d2
        return d1 if d1 > d2 else d2

    if not resources:
        return [0, 0]

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_t = None
    best_val = -10**18
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        center = -0.08 * (abs(tx - cx) + abs(ty - cy))
        advantage = (opd - myd)  # positive if we're closer
        val = 3.0 * advantage - 0.35 * myd + center
        if val > best_val:
            best_val = val
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_move_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1

        if (nx, ny) in obstacles:
            continue  # avoid stepping into obstacle; if engine blocks, this move is inferior anyway

        myd2 = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        advantage2 = opd - myd2

        # small tie-break: prefer moves that get us closer to the target, and slightly keep away from obstacles
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                    near_obs += 1

        move_val = 3.0 * advantage2 - 0.45 * myd2 - 0.12 * near_obs
        if move_val > best_move_val:
            best_move_val = move_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]