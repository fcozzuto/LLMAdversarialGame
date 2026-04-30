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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets we can reach first; if none, prefer closest contest.
            score = ds - do
            if best is None or score < best[0] or (score == best[0] and (ds < best[1])):
                best = (score, ds, rx, ry)
        _, _, tx, ty = best
    else:
        # No visible resources: drift toward farthest corner from opponent.
        tx, ty = (0, 0) if cheb(sx, sy, 0, 0) + cheb(ox, oy, w - 1, h - 1) < cheb(sx, sy, w - 1, h - 1) + cheb(ox, oy, 0, 0) else (w - 1, h - 1)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Minimize target distance; break ties by maximizing opponent distance; deterministic tie-break by dx,dy order.
        val = (d_to_target, -d_opp)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]