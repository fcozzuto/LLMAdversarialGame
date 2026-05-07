def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    resources = observation.get("resources") or []
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = valid[0]
        bestd = dist(best[2], best[3], tx, ty)
        for cand in valid[1:]:
            d = dist(cand[2], cand[3], tx, ty)
            if d < bestd:
                bestd = d; best = cand
        return [best[0], best[1]]

    scored = []
    for dx, dy, nx, ny in valid:
        best_my = 10**9
        best_opp = 10**9
        best_gap = -10**9
        best_res = None
        best_d_my = 10**9
        # choose resource maximizing "I can beat opponent by moving here"
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            gap = opd - myd  # positive means I am closer after this move
            if gap > best_gap or (gap == best_gap and (myd < best_d_my or (myd == best_d_my and (rx, ry) < best_res if best_res is not None else True))):
                best_gap = gap
                best_my = myd
                best_opp = opd
                best_res = (rx, ry)
                best_d_my = myd

        # secondary: if can't beat anyone, go to closest resource overall but penalize those opponent is closer to
        # compute a final value to maximize deterministically
        closest_my = min(dist(nx, ny, rx, ry) for rx, ry in resources)
        closest_opponent = min(dist(ox, oy, rx, ry) for rx, ry in resources)
        opp_pen = 0
        for rx, ry in resources:
            opd = dist(ox, oy, rx, ry)
            myd = dist(nx, ny, rx, ry)
            if opd < myd:
                opp_pen += 1
        value = (best_gap * 1000) - (closest_my * 3) - opp_pen * 5 + (0 if closest_opponent == 0 else 0)
        scored.append((value, -best_my, -best_opp, dx, dy))
    scored.sort(reverse=True)
    return [scored[0][3], scored[0][4]]