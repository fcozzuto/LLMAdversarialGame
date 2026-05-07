def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def bounds_clamp_target():
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        tx = cx
        ty = cy
        if sx <= cx: tx = min(gw - 2, max(1, cx - 1))
        if sx > cx: tx = min(gw - 2, max(1, cx + 1))
        if sy <= cy: ty = min(gh - 2, max(1, cy - 1))
        if sy > cy: ty = min(gh - 2, max(1, cy + 1))
        return tx, ty

    if not resources:
        tx, ty = bounds_clamp_target()
        best = (None, -10**18)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > best[1]:
                best = ((dx, dy), v)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    best_move = [0, 0]
    best_val = -10**18
    best_my_d = 10**9

    # Evaluate each move by the best resource "swing": (opp_dist - my_dist), prefer lower my_dist when tied.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_best = 10**9
        swing_best = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            swing = opp_d - my_d
            if swing > swing_best or (swing == swing_best and my_d < my_best):
                swing_best = swing
                my_best = my_d
        # Slightly prefer moves that reduce our distance to the currently best candidate overall
        # and avoid drifting when ahead.
        ahead = (min(cheb(sx, sy, r[0], r[1]) for r in resources) <= min(cheb(ox, oy, r[0], r[1]) for r in resources))
        drift_pen = 0.1 * (1 if dx != 0 and dy != 0 else 0)
        v = swing_best - 0.01 * my_best - drift_pen + (0.05 if ahead and swing_best >= 0 else 0.0)
        if v > best_val or (v == best_val and my_best < best_my_d):
            best_val = v
            best_my_d = my_best
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]