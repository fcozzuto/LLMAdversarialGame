def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {tuple(p) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1
        best = (10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = md(nx, ny, tx, ty)
            cand = (d, 0 if dx == 0 and dy == 0 else 1, dx, dy)
            if cand < best:
                best = (d, 0, dx, dy)
        return [best[2], best[3]]

    res = [tuple(r) for r in resources]

    best_move = (0, 0)
    best_key = (10**18, 10**18, 10**18, 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_min = 10**9
        op_min = 10**9
        for rx, ry in res:
            d1 = md(nx, ny, rx, ry)
            if d1 < my_min:
                my_min = d1
            d2 = md(ox, oy, rx, ry)
            if d2 < op_min:
                op_min = d2

        # Prefer moves that increase advantage and also reduce our closest distance
        advantage = op_min - my_min
        # Secondary: prefer moving toward the "best" target under current advantage metric
        target_key = (10**18, 10**18, 10**18)
        for rx, ry in res:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            key = (-(do - ds), ds, rx + 100 * ry)
            if key < target_key:
                target_key = key

        cand_key = (-advantage, target_key[0], target_key[1], nx, ny)
        if cand_key < best_key:
            best_key = cand_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]