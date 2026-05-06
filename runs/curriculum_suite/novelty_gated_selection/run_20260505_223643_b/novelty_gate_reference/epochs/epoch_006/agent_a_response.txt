def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_now = -10**18
        best_t = (ox, oy)
        for rx, ry in resources:
            myd0 = cd(x, y, rx, ry)
            opd0 = cd(ox, oy, rx, ry)
            sc0 = 10 * (opd0 - myd0) - myd0
            if sc0 > best_now:
                best_now = sc0
                best_t = (rx, ry)

        tx, ty = best_t
        opp_close = cd(x, y, ox, oy) <= 2
        deny_bias = 2 if opp_close else 0
    else:
        tx, ty = ox, oy
        deny_bias = 2

    def eval_cell(nx, ny):
        if resources:
            # Choose best resource for next step, but include opponent reach pressure
            best = -10**18
            for rx, ry in resources:
                myd = cd(nx, ny, rx, ry)
                opd = cd(ox, oy, rx, ry)
                # prefer own quick reach, and resources opponent can't reach soon
                sc = 10 * (opd - myd) - myd
                # if we can step onto a resource, huge bump
                if nx == rx and ny == ry:
                    sc += 50
                # slight preference to reduce our distance to the selected "focus" target
                sc += -0.5 * cd(nx, ny, tx, ty)
                if sc > best:
                    best = sc
            # If no strong resource advantage, move to deny: closer to opponent
            best += deny_bias * (-cd(nx, ny, ox, oy))
            return best
        else:
            return -cd(nx, ny, ox, oy)

    best_move = (0, 0)
    best_val = -10**18
    for dxm, dym in moves:
        nx, ny = x + dxm, y + dym
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = eval_cell(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dxm, dym)

    dxm, dym = best_move
    return [int(dxm), int(dym)]