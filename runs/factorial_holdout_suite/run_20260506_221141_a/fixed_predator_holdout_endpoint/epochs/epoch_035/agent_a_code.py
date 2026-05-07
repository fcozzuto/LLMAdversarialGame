def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        v = a - c
        if v < 0:
            v = -v
        u = b - d
        if u < 0:
            u = -u
        return v + u

    # Pick a target that maximizes advantage; prefer nearer when roughly equal.
    best_t = None
    best_key = None
    for tx, ty in res:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # Advantage first; if opponent already much closer, de-prioritize heavily.
        key = (do - ds, -(min(ds, do)), -ds)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    # Move greedily toward target but avoid obstacles; if blocked, try alternative step minimizing distance.
    primary_dx = 0 if tx == sx else (1 if tx > sx else -1)
    primary_dy = 0 if ty == sy else (1 if ty > sy else -1)
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    best_move = None
    best_dist = None
    for dx, dy, nx, ny in candidates:
        d = man(nx, ny, tx, ty)
        # Prefer primary direction if tied, but keep deterministic ordering.
        tie = (dx == primary_dx and dy == primary_dy)
        if best_dist is None or d < best_dist or (d == best_dist and tie and not (best_move[0] == primary_dx and best_move[1] == primary_dy)):
            best_dist = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]