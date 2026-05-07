def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    turns_remaining = observation.get("turns_remaining", 0)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 2 if sx < gw // 2 else 1
        ty = gh - 2 if sy < gh // 2 else 1
        cx, cy = gw // 2, gh // 2
        if cheb(sx, sy, tx, ty) > cheb(sx, sy, cx, cy):
            tx, ty = cx, cy
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Pick move maximizing lead on the best available resource.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        cur_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Strong preference: resources we can reach not later than opponent.
            lead = opd - myd
            # Encourage earlier collection within horizon.
            horizon = 0
            if turns_remaining is not None and turns_remaining > 0:
                if myd <= turns_remaining:
                    horizon = 2
                if opd <= turns_remaining:
                    horizon -= 1
            v = 10 * lead - myd + horizon
            if (opd - myd) >= 0:
                v += 5
            if v > cur_best:
                cur_best = v
        if cur_best > best_val:
            best_val = cur_best
            best_move = [dx, dy]
    return best_move