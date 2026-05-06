def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not free(sx, sy):
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    target = None
    best = None
    # Race resources where we have tempo advantage; avoid chasing clearly-opponent-owned cells.
    for rx, ry in res:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # If opponent is much closer, deprioritize.
        tempo = od - sd
        # Prefer nearer resources when tempo is similar; prefer breaking ties by x,y deterministically.
        key = (tempo, -sd, -rx, -ry)
        if best is None or key > best:
            best = key
            target = (rx, ry)

    if target is None:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx, ty = int(round(cx)), int(round(cy))
    else:
        tx, ty = target

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If the direct step is blocked, take the best alternative that still reduces distance to target,
    # with a small preference for moving away from opponent to reduce contesting.
    direct = (sx + dx, sy + dy)
    if free(*direct):
        return [dx, dy]

    best_move = (0, 0)
    best_score = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not free(nx, ny):
            continue
        d_to_t = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        score = (-d_to_t, d_opp, -mx, -my)  # deterministic tie-break
        if best_score is None or score > best_score:
            best_score = score
            best_move = (mx, my)
    return [int(best_move[0]), int(best_move[1])]