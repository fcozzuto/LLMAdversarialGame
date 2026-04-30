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

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = dist(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best or (0, 0))

    # Choose targets that favor our access while discouraging opponent access.
    best_t = None
    best_ts = 10**18
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        ts = ds - 0.65 * do
        if ts < best_ts:
            best_ts = ts
            best_t = (rx, ry)

    opp_t = min(resources, key=lambda r: abs(r[0] - ox) + abs(r[1] - oy))

    tx, ty = best_t
    otx, oty = opp_t

    # Pick move that reduces our distance to our target and increases opponent distance to theirs.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = abs(tx - nx) + abs(ty - ny)
        opdd = abs(otx - nx) + abs(oty - ny)
        # Primary: minimize myd; Secondary: maximize opdd; Small tie-break to keep away from opponent.
        v = (-1000 * myd) + (10 * opdd) + (dist(nx, ny, ox, oy) * 0.001)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]