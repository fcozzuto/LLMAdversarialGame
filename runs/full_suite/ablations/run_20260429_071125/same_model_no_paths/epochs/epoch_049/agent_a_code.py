def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not ok(sx, sy):
        for dx, dy in moves:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Choose best resource by advantage: (opp_dist - my_dist), tie-break by my_dist
    if resources:
        best = None
        best_score = None
        best_myd = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            score = opd - myd
            if best is None or score > best_score or (score == best_score and myd < best_myd):
                best = (rx, ry)
                best_score = score
                best_myd = myd
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    # Pick move that minimizes my distance to target; tie-break by maximizing opponent distance advantage
    best_move = (0, 0)
    best_val = None
    best_opp = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        val = (myd, -opd)  # smaller myd, larger opd
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
            best_opp = opd

    return [int(best_move[0]), int(best_move[1])]