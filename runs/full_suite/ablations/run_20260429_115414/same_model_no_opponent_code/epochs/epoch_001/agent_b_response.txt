def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"] if observation.get("resources") is not None else []
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**9, 0, 0)

    target = None
    if resources:
        best_t = (-10**9, None)
        for r in resources:
            sdist = dist((sx, sy), (r[0], r[1]))
            odist = dist((ox, oy), (r[0], r[1]))
            score = (odist - sdist) * 10 - sdist  # prefer where we're closer
            if r[0] == sx and r[1] == sy:
                score += 10**6
            if score > best_t[0] or (score == best_t[0] and (r[0], r[1]) < best_t[1]):
                best_t = (score, r)
        target = best_t[1]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if target is None:
        tx, ty = cx, cy
    else:
        tx, ty = target[0], target[1]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources and (nx, ny) in set((p[0], p[1]) for p in resources):
            score = 10**9
        else:
            nd = dist((nx, ny), (tx, ty))
            od = dist((ox, oy), (tx, ty)) if target is not None else 0
            # also mildly discourage moving toward opponent to avoid handoffs
            score = -nd * 100 + (od - dist((ox, oy), (nx, ny))) * 2
            # slight tie-break toward progressing direction deterministically
            score -= abs(nx - tx) + abs(ny - ty) * 0.001
        # deterministic tie-break by move ordering
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    dx, dy = best[1], best[2]
    if (sx + dx, sy + dy) in obstacles or not in_bounds(sx + dx, sy + dy):
        return [0, 0]
    return [dx, dy]