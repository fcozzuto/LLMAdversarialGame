def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_d = cheb(sx, sy, ox, oy)

    best = None
    best_score = -10**18
    ti = int(observation.get("turn_index") or 0)
    for dx, dy, nx, ny in legal:
        if resources:
            my_best = 10**9
            op_best = 10**9
            my_target = None
            for rx, ry in resources:
                dmy = cheb(nx, ny, rx, ry)
                if dmy < my_best:
                    my_best = dmy
                    my_target = (rx, ry)
                dop = cheb(ox, oy, rx, ry)
                if dop < op_best:
                    op_best = dop
            my_progress = -my_best
            opp_progress = -op_best
            # Prefer moves that reduce my distance to the "most competitive" target when tied on my_best
            competitive_pen = 0
            if my_target is not None:
                dr = cheb(nx, ny, my_target[0], my_target[1]) - cheb(sx, sy, my_target[0], my_target[1])
                competitive_pen = dr * 0.1
            # Avoid getting too close to opponent if it doesn't improve resource access
            threat = 0
            nd_opp = cheb(nx, ny, ox, oy)
            if nd_opp < opp_d:
                threat = (opp_d - nd_opp) * 0.05
            score = (my_progress - opp_progress * 0.9) - competitive_pen - threat
        else:
            # No visible resources: move to reduce distance to opponent to contest center-ish
            score = -cheb(nx, ny, w // 2, h // 2) * 0.2 + (opp_d - cheb(nx, ny, ox, oy)) * 0.1
        # Deterministic tie-break
        score = score * 1000 + (dx + 2) * 10 + (dy + 2) + ((nx * 8 + ny + ti) % 3) * 0.01
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]