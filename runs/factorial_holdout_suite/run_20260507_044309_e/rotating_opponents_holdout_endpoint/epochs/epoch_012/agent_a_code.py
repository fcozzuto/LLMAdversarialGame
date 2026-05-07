def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    best_key = None
    best_t = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        reach_first = 1 if myd <= opd else 0
        score = reach_first * 1000000 + (opd - myd) * 50 - myd * 2
        pen = 0
        for adx, ady in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (rx + adx, ry + ady) in obstacles:
                pen += 1
        score -= pen
        key = (-(reach_first), -score, myd, opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    dx = 0 if sx == rx else (1 if rx > sx else -1)
    dy = 0 if sy == ry else (1 if ry > sy else -1)

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                continue
            nx, ny = sx + mx, sy + my
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((cheb(nx, ny, rx, ry), mx, my))
    candidates.append((cheb(sx + dx, sy + dy, rx, ry) if in_bounds(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles else 10**9, dx, dy))
    candidates.append((cheb(sx, sy, rx, ry) + 1, 0, 0))

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]