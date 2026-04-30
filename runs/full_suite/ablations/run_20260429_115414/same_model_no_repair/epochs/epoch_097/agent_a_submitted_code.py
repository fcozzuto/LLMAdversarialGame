def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    if (sx, sy) in blocked:
        return [0, 0]
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates_pos = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            candidates_pos.append((nx, ny, dx, dy))

    if not candidates_pos:
        candidates_pos = [(sx, sy, 0, 0)]

    def obstacle_pen(x, y):
        pen = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                pen += 10000
            elif d == 1:
                pen += 8
            elif d == 2:
                pen += 3
        return pen

    opp_dist_cache = []
    for rx, ry in resources:
        opp_dist_cache.append(cheb(ox, oy, rx, ry))

    best_target = None
    best_key = None
    for i, (rx, ry) in enumerate(resources):
        if (rx, ry) in blocked:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = opp_dist_cache[i]
        if myd == 0:
            best_target = (rx, ry)
            best_key = (-10**9, 0)
            break
        # Prefer resources I can reach earlier than opponent; otherwise still allow if close.
        rel = myd - opd
        key = (rel, myd + obstacle_pen(rx, ry) * 0.2)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    def score_move(nx, ny):
        if (nx, ny) in blocked:
            return 10**12
        myd = cheb(nx, ny, tx, ty)
        # Reduce giving opponent a better angle: if opponent is closer to target, increase cost.
        opd = cheb(ox, oy, tx, ty)
        # Prefer moving to positions that keep opponent at distance (not too strict).
        opp_close = cheb(nx, ny, ox, oy)
        # Encourage capturing sooner and avoid obstacles.
        return myd * 10 + obstacle_pen(nx, ny) + (opd - myd) * (-1) + (7 / (opp_close + 1))

    best = None
    best_s = None
    for nx, ny, dx, dy in candidates_pos:
        s = score_move(nx, ny)
        if best_s is None or s < best_s or (s == best_s and (dx, dy) < (best[2], best[3])):
            best_s = s
            best = (nx, ny, dx, dy)

    return [best[2], best[3]]