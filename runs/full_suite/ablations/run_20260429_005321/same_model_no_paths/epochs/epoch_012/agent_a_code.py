def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except Exception:
            pass

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        try:
            res.append((r[0], r[1]))
        except Exception:
            pass

    if any((sx == rx and sy == ry) for rx, ry in res):
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    adj = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    target = None
    if res:
        bestd = 10**9
        for x, y in res:
            d = man(sx, sy, x, y)
            if d < bestd:
                bestd = d
                target = (x, y)
    if target is None:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestv = -10**9
        for tx, ty in corners:
            v = man(ox, oy, tx, ty) - 0.5 * man(sx, sy, tx, ty)
            if v > bestv:
                bestv = v
                target = (tx, ty)

    tx, ty = target
    best_move = [0, 0]
    best_score = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            if (nx, ny) == (sx, sy):
                stay_bonus = 0.2
            else:
                stay_bonus = 0.0
            d_to = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ox, oy)
            block_pen = 0
            for ax, ay in adj:
                if (nx + ax, ny + ay) in obs:
                    block_pen += 1
            score = (-d_to) + 0.08 * d_opp - 0.35 * block_pen + stay_bonus
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move