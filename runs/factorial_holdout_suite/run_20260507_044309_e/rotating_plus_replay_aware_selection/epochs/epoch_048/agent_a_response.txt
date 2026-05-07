def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    tr = observation.get("turns_remaining", 0) or 0

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            k = (d, cheb(ox, oy, tx, ty))
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    best_key = None
    best_move = [0, 0]
    center_bias = (w + h) * 0.01
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds0 = cheb(sx, sy, rx, ry)
        do0 = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; otherwise pick those that slow/avoid giving opponent.
        # Key: (who's closer, opponent closeness, prefer closer target, slight center bias)
        # Smaller is better.
        base_key = (ds0 - do0, do0, ds0, (rx - w/2)*(rx - w/2) + (ry - h/2)*(ry - h/2))
        # Evaluate best move toward this target.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            ds = cheb(nx, ny, rx, ry)
            do = do0  # opponent static approximation per-turn
            key = (ds - do, do, ds, base_key[3], center_bias * (abs(nx - w/2) + abs(ny - h/2)))
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]

    # If opponent is currently closer to our chosen target and time is short, fall back to maximizing our nearest-win.
    if tr <= 6:
        nearest_win_ds = None
        nearest_win = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds <= do:
                if nearest_win_ds is None or ds < nearest_win_ds:
                    nearest_win_ds = ds
                    nearest_win = (rx, ry)
        if nearest_win is not None:
            rx, ry = nearest_win
            best_key2 = None
            best_move2 = [0, 0]
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not legal(nx, ny):
                    continue
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                key2 = (ds - do, ds)
                if best_key2 is None or key2 < best_key2:
                    best_key2 = key2
                    best_move2 = [dx, dy]
            best_move = best_move2

    return [int(best_move[0]), int(best_move[1])]