def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def kingd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manhd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    target = None
    if resources:
        best = None
        for tx, ty in resources:
            ds = kingd(sx, sy, tx, ty)
            do = kingd(ox, oy, tx, ty)
            score = ds - 0.85 * do
            cand = (score, ds + do, tx, ty)
            if best is None or cand < best:
                best = cand
                target = (tx, ty)
    else:
        target = (cx, cy)

    tx, ty = int(target[0]), int(target[1])
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        on_res = 1.0 if (nx, ny) == (tx, ty) and (nx, ny) in resources else 0.0
        d_self = kingd(nx, ny, tx, ty)
        d_opp = kingd(nx, ny, ox, oy)
        d_center = manhd(nx, ny, cx, cy)

        # Prefer reaching target, staying safer from the opponent, and avoiding crowding the opponent.
        val = (-1.4 * d_self) + (0.18 * d_opp) + (-0.06 * d_center) + (2.0 * on_res)

        # Small deterministic tie-break: prefer lexicographically smaller move.
        tie = (val, -dx, -dy, nx, ny)
        if best_val is None or tie > best_val:
            best_val = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]