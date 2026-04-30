def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    if not resources:
        return [0, 0]

    def sgn(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best = None
    best_metric = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist2((sx, sy), (rx, ry))
        do = dist2((ox, oy), (rx, ry))
        metric = ds + (120 if do < ds else 0) + (0.1 * (ds - do) if do < ds else 0)
        if best_metric is None or metric < best_metric:
            best_metric = metric
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= observation["grid_width"] or ny >= observation["grid_height"]:
                continue
            if (nx, ny) in obstacles:
                continue
            dnew = dist2((nx, ny), (tx, ty))
            # Prefer moves that get closer; tie-break deterministically by opponent distance and then dx/dy
            do_new = dist2((nx, ny), (ox, oy))
            score = (dnew, abs(do_new - dist2((sx, sy), (ox, oy))), dx * 3 + dy)
            cand.append((score, [dx, dy]))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: t[0])
    return cand[0][1]