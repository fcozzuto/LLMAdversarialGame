def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def near_obst_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obst:
                    p += 1
        return p

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Evaluate moves by minimizing our advantage gap for the most contested resource.
        # Score: we want (d_self - d_opp) to be small; if negative, we are closer.
        move_val = 0
        cur_best_gap = 10**18
        cur_best_ds = 10**18

        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            gap = d_self - d_opp
            # Prefer resources we can reach sooner (smaller d_self),
            # but primarily reduce gap against the opponent.
            if gap < cur_best_gap or (gap == cur_best_gap and d_self < cur_best_ds):
                cur_best_gap = gap
                cur_best_ds = d_self

        # Additional tie-breaking: prefer general progress toward the nearest resource.
        nearest_ds = 10**18
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            ds = cheb(nx, ny, rx, ry)
            if ds < nearest_ds:
                nearest_ds = ds

        # Penalties to avoid obstacle-adjacent dead-ends and reduce reckless chasing.
        obst_pen = near_obst_pen(nx, ny)
        # Small reward for improving our position vs current step (encourages decisive movement).
        cur_nearest = 10**18
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            ds = cheb(sx, sy, rx, ry)
            if ds < cur_nearest:
                cur_nearest = ds
        progress = cur_nearest - nearest_ds

        # Compose value deterministically.
        move_val = (-cur_best_gap * 100) + (progress * 10) + (-obst_pen * 3) + (-nearest_ds)

        if move_val > best_val:
            best_val = move_val
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]]