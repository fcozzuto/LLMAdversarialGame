def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if (sx, sy) in set(res):
        return [0, 0]
    if not res:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    op = (ox, oy)

    best = None
    best_key = None
    for r in res:
        dm = man(my, r)
        do = man(op, r)
        # Prefer contests we can reach first; add bias to resources near opponent's sweep lane (same y),
        # which helps against row-sweeping policies.
        lane_bias = -2 if r[1] == oy else 0
        # Deterministic tie-break by coordinates.
        key = (-(do - dm) + lane_bias, -dm, r[0], r[1])
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy, (nx, ny)))

    if not legal:
        return [0, 0]

    # Greedy step toward target, with small penalty for moving away and for approaching obstacles too closely.
    def obstacle_penalty(nx, ny):
        pen = 0
        for ax, ay in obs:
            d = abs(ax - nx) + abs(ay - ny)
            if d == 1:
                pen += 3
            elif d == 2:
                pen += 1
        return pen

    best_move = None
    best_mkey = None
    for dx, dy, (nx, ny) in legal:
        dcur = man(my, (tx, ty))
        dnext = man((nx, ny), (tx, ty))
        # prefer decrease in distance; prefer staying closer if equal.
        mkey = (-(dnext - dcur), -dnext, -obstacle_penalty(nx, ny), nx, ny, dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]