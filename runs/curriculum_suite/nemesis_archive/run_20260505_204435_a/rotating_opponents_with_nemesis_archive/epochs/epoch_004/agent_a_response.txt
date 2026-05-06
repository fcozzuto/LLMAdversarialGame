def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def cheb(ax, ay, bx, by):
        da = ax - bx; db = ay - by
        if da < 0: da = -da
        if db < 0: db = -db
        return da if da > db else db

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, cx, cy)
            key = (d, cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Pick a resource where we are (deterministically) advantaged over the opponent.
    best_target = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        key = (-adv, ds, do, rx, ry)
        if best_target is None or key < best_target[0]:
            best_target = (key, rx, ry)
    _, tx, ty = best_target[0], best_target[1], best_target[2]

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds_next = cheb(nx, ny, tx, ty)
        do_next = cheb(ox, oy, tx, ty)
        # Reward reducing our distance to the target; if we're behind, prioritize distance from opponent a bit.
        score1 = ds_next
        score2 = -cheb(nx, ny, ox, oy) if (do_next <= ds_next) else cheb(nx, ny, ox, oy)
        key = (score1, score2, abs(dx) + abs(dy), dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [best_move[1], best_move[2]] if best_move else [0, 0]