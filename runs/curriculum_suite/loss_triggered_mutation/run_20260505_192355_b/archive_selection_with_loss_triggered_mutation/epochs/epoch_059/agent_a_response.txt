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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    cur_free = free(sx, sy)
    if not cur_free:
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not res:
        tx, ty = ox, oy
    else:
        # Choose a resource where we are at least not worse; otherwise pick the least-lost.
        best = None
        for rx, ry in res:
            myd = d((sx, sy), (rx, ry))
            opd = d((ox, oy), (rx, ry))
            # Prefer winning contest; break ties toward closer overall and toward deterministic tie order.
            key = (opd - myd, -(myd + opd), (rx + 3 * ry))
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        _, (tx, ty) = best

        # If opponent is clearly closer to all resources, directly pressure the opponent.
        # (This changes behavior from pure collection to interception.)
        my_best = 10**9
        op_best = 10**9
        for rx, ry in res:
            my_best = min(my_best, d((sx, sy), (rx, ry)))
            op_best = min(op_best, d((ox, oy), (rx, ry)))
        if op_best + 1 < my_best:
            tx, ty = ox, oy

    # Move one step toward (tx, ty), but never into obstacles.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    cand = (sx + dx, sy + dy)
    if free(*cand):
        return [dx, dy]

    bestm = None
    bestkey = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not free(nx, ny):
            continue
        dist_to = d((nx, ny), (tx, ty))
        # Prefer not moving away; then minimal distance; deterministic tie via coordinates.
        key = (-dist_to, abs(mdx) + abs(mdy), nx - ny)
        if bestkey is None or key > bestkey:
            bestkey = key
            bestm = (mdx, mdy)
    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]