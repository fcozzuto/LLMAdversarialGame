def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        ax, ay = a, b
        bx, by = c, d
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da > db else db

    # Choose resource where we are relatively closer than the opponent; deterministic tie-breaks.
    best_res = None
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        key = (myd - opd, myd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (tx, ty)

    tx, ty = best_res
    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]

    # Evaluate moves: minimize our remaining distance, then maximize opponent's distance to the same target.
    best_move = (0, 0)
    best_eval = None
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            my_after = cheb(nx, ny, tx, ty)
            op_after = cheb(ox, oy, tx, ty)
            # opponent doesn't move this turn; still helps deterministic ordering via our move options
            # add small tie-break to avoid oscillation: prefer staying closer to opponent (more blocking) if equal
            block_bias = abs(nx - ox) + abs(ny - oy)
            ev = (my_after, -op_after, block_bias, dx, dy)
            if best_eval is None or ev < best_eval:
                best_eval = ev
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]