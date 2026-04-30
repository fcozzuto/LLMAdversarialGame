def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            candidates.append((dx, dy, nx, ny))

    # If somehow no legal move, stay.
    if not candidates:
        return [0, 0]

    # No resources: drift to improve distance to opponent (deterministic escape).
    if not resources:
        best = None
        for dx, dy, nx, ny in candidates:
            s = -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
            if best is None or (s, dx, dy) > (best[0], best[1], best[2]):
                best = (s, dx, dy)
        return [best[1], best[2]]

    # Score each move by best contested target and proximity bonuses.
    best_score = None
    best_move = (0, 0)
    for dx, dy, nx, ny in candidates:
        # primary: pick target where we are closer than opponent (dself - dopp small)
        d_best = None
        for r in resources:
            dself = dist((nx, ny), r)
            dopp = dist((ox, oy), r)
            # prefer smaller (dself - dopp) and overall closeness
            key = (dself - dopp, dself)
            if d_best is None or key < d_best[0]:
                d_best = (key, r)
        target = d_best[1]
        dself_t = d_best[0][1]

        # secondary: avoid letting opponent be closer to many resources (pressure)
        # top-k resources by distance from us
        rs = []
        for r in resources:
            rs.append((dist((nx, ny), r), dist((ox, oy), r)))
        rs.sort(key=lambda t: t[0])
        k = 4 if len(rs) >= 4 else len(rs)
        pressure = 0
        for i in range(k):
            ds, do = rs[i]
            # higher when opponent is relatively far
            pressure += (do - ds) / (1 + ds)

        # also gently bias toward staying away from obstacles already (implicitly via legality),
        # and toward reaching target.
        score = 1000.0 * (-dself_t) + 50.0 * pressure

        # deterministic tie-break: prefer lexicographically larger (dx,dy) among equal scores
        if best_score is None or (score, dx, dy) > (best_score, best_move[0], best_move[1]):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]