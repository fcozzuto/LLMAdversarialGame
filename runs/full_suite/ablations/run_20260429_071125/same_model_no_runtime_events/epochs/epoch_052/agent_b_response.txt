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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    legal = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if resources:
        best_t = None
        best_val = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            if ds == 0:
                val = -1000000.0
            else:
                val = ds + 0.35 * do
            if best_val is None or val < best_val or (val == best_val and (tx, ty) < best_t):
                best_val, best_t = val, (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = int(round(cx)), int(round(cy))

    best_move = None
    best_score = None
    prev_ds = cheb(sx, sy, tx, ty)
    prev_do = cheb(ox, oy, tx, ty)
    opp_dist_self = cheb(sx, sy, ox, oy)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        opp_self_after = cheb(nx, ny, ox, oy)

        # Primary: get closer to target (with tie-break by taking/near-taking).
        # Secondary: deny opponent access by making our approach rate better relative to opponent.
        # Tertiary: keep some distance from opponent to avoid being outpaced during contests.
        score = 0.0
        score += (prev_ds - ds) * 10.0
        if ds == 0:
            score += 500.0
        score += (prev_do - do) * 1.5
        score += (opp_self_after - opp_dist_self) * 0.8
        score += cheb(nx, ny, tx, ty) * (-0.3)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]