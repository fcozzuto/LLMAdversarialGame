def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_r = None
    best_adv = None
    best_myd = None
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # positive means we're closer
        if best_adv is None or adv > best_adv or (adv == best_adv and (best_myd is None or myd < best_myd)):
            best_adv, best_myd, best_r = adv, myd, (rx, ry)

    tr, ty = best_r
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = None

    def near_obstacle(x, y):
        # count adjacent obstacles (including diagonals)
        cnt = 0
        for ax in (-1, 0, 1):
            nx = x + ax
            if nx < 0 or nx >= w: continue
            for ay in (-1, 0, 1):
                ny = y + ay
                if ny < 0 or ny >= h: continue
                if (nx, ny) in obs:
                    cnt += 1
        return cnt

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        myd2 = cheb(nx, ny, tr, ty)
        opd2 = cheb(ox, oy, tr, ty)
        # Prefer getting closer to target, and making us relatively closer than opponent.
        adv2 = opd2 - myd2
        target_score = myd2 * 10 - adv2  # smaller is better
        obst_pen = near_obstacle(nx, ny)
        score = target_score + obst_pen
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]