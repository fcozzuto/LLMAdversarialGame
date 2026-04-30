def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_t = None
    best_val = None
    for (rx, ry) in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        val = myd - 0.9 * opd
        if best_val is None or val < best_val or (val == best_val and (myd < best_t[0] if best_t else True)):
            best_val = val
            best_t = (myd, rx, ry)

    _, tx, ty = best_t
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) in resources:
            return [dx, dy]
        myd2 = cheb(nx, ny, tx, ty)
        # obstacle proximity penalty (discourage squeezing near obstacles)
        ob_pen = 0
        for ox2 in (-1, 0, 1):
            for oy2 in (-1, 0, 1):
                if ox2 == 0 and oy2 == 0:
                    continue
                if (nx + ox2, ny + oy2) in obstacles:
                    ob_pen += 0.35
        # mild opponent avoidance: discourage moving closer to opponent when not improving target
        oppd2 = cheb(nx, ny, ox, oy)
        opp_pen = 0.12 * (oppd2 == 0) + 0.06 * (oppd2 < cheb(sx, sy, ox, oy))
        # prefer staying within grid and making progress toward target
        score = myd2 + ob_pen + opp_pen
        # deterministic tie-break: lexicographic order via move index
        cand.append((score, dx, dy, myd2, ob_pen, opp_pen))

    cand.sort(key=lambda z: (z[0], z[1], z[2]))
    return [int(cand[0][1]), int(cand[0][2])]