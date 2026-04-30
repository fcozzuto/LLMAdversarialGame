def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    # If currently on blocked cell, escape deterministically.
    if (sx, sy) in blocked:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose best resource: prefer those we're closer to than opponent.
    best = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Lower is better: go for favorable resources, not ones opponent likely grabs.
        score = ds - (do * 0.7) + ((rx + ry) * 0.01)
        if best_score is None or score < best_score:
            best_score = score
            best = (rx, ry)

    def next_step_toward(tx, ty):
        best_step = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # Break ties: keep some separation from opponent and avoid oscillations by favoring x+y.
            opp_d = cheb(nx, ny, ox, oy)
            val = (d, -opp_d, (nx + ny) * 0.001, dx*dx + dy*dy)
            if best_val is None or val < best_val:
                best_val = val
                best_step = (dx, dy)
        return list(best_step)

    if best is not None:
        return next_step_toward(best[0], best[1])

    # No resources visible: move toward center while staying away from opponent if possible.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_step = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dcent = cheb(nx, ny, cx, cy)
        do = cheb(nx, ny, ox, oy)
        val = (dcent, -do, (nx + ny) * 0.001, dx*dx + dy*dy)
        if best_val is None or val < best_val:
            best_val = val
            best_step = (dx, dy)
    return [best_step[0], best_step[1]]