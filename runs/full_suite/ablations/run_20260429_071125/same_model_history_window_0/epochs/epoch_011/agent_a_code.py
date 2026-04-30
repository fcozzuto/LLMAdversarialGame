def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]

    obs_set = {(x, y) for x, y in obstacles}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dy == 0 else (dy if dy >= 0 else -dy) if dx == 0 else (dx if dx >= 0 else -dx if dy == 0 else None)

    # simpler chebyshev
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # choose target resource that we are best positioned for
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) == (sx, sy):
                continue
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            key = (ds, do)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1] if best is not None else (resources[0][0], resources[0][1])

    # if no target, move away from opponent while staying valid
    if target is None:
        tx, ty = sx, sy
    else:
        tx, ty = target

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        if (nx, ny) == (ox, oy):
            pass
        if target is None:
            score = dist(nx, ny, ox, oy)
        else:
            d_to_t = dist(nx, ny, tx, ty)
            # prefer moves that also don't let opponent get much closer
            d_opp = dist(ox, oy, tx, ty)
            score = (-d_to_t, (d_to_t - d_opp))
        candidates.append((score, (dx, dy)))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda z: (z[0][0] if isinstance(z[0], tuple) else z[0]), reverse=False)
    # handle both tuple and int score deterministically
    best_dxdy = None
    best_key = None
    for score, dxy in candidates:
        if isinstance(score, tuple):
            key = (score[0], score[1], dxy[0], dxy[1])
        else:
            key = (-score, dxy[0], dxy[1])
        if best_key is None or key < best_key:
            best_key = key
            best_dxdy = dxy

    return [int(best_dxdy[0]), int(best_dxdy[1])]