def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev: matches diagonal movement

    # Prefer moves that let us reach some resource sooner than opponent.
    best = (-10**9, 10**9, (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Evaluate only nearby resources first for determinism/speed
        candidates = []
        for rx, ry in resources:
            dself = dist(nx, ny, rx, ry)
            if dself <= 6:  # keep it tight
                candidates.append((rx, ry, dself))
        if not candidates:
            candidates = [(rx, ry, dist(nx, ny, rx, ry)) for (rx, ry) in resources]

        # Choose best resource after this move
        local_best = None
        local_metric = -10**9
        local_tie = 10**9
        for rx, ry, dself in candidates:
            dopp = dist(ox, oy, rx, ry)
            # primary: how much earlier we can arrive; secondary: earlier arrival; tertiary: block (bigger opp distance)
            metric = (dopp - dself)
            if metric > local_metric or (metric == local_metric and (dself < local_tie or (dself == local_tie and dopp > dist(sx, sy, rx, ry)))):
                local_metric = metric
                local_tie = dself
                local_best = (rx, ry, dself, dopp)
        # Encourage not stepping away unnecessarily
        away = abs(nx - sx) + abs(ny - sy)
        overall = (local_metric, -local_tie, -away)
        if overall[0] > best[0] or (overall[0] == best[0] and overall[1] > -best[1]):
            best = (overall[0], -overall[1], (dx, dy))
    return [best[2][0], best[2][1]]