def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    tx, ty = (w - 1) // 2, (h - 1) // 2
    if resources:
        best_move = (0, 0)
        best_score = -10**18
        # Strategy: for each candidate move, pick the resource that maximizes (opp_dist - my_dist),
        # with a tie-break preferring smallest my_dist.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            chosen = None
            chosen_my = 10**9
            chosen_gap = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                gap = opd - myd
                if gap > chosen_gap or (gap == chosen_gap and myd < chosen_my):
                    chosen_gap = gap
                    chosen_my = myd
                    chosen = (rx, ry)
            # Include slight preference to reduce distance to that chosen resource from current pos,
            # and to not move away from the board center too aggressively.
            if chosen is None:
                continue
            myd_now = cheb(sx, sy, chosen[0], chosen[1])
            center_bias = -abs(nx - tx) - abs(ny - ty)
            score = chosen_gap * 100 - myd_now * 10 + center_bias
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # If no resources remain, stabilize near center
    best = None
    bestd = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < bestd:
            bestd = d
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]