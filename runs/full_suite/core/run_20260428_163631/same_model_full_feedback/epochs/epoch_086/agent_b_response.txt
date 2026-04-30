def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in obstacles:
        obstacles.discard((sx, sy))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick target resource where we are relatively closer than opponent.
    if resources:
        best_t = resources[0]
        best_s = 10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            s = ds - int(0.85 * do)
            if s < best_s or (s == best_s and ds < cheb(sx, sy, best_t[0], best_t[1])):
                best_s = s
                best_t = (rx, ry)
    else:
        # No visible resources: drift toward center while keeping away from opponent.
        best_t = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = best_t

    # Choose move that reduces distance to target; tie-break by moving away from opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dtarget = cheb(nx, ny, tx, ty)
        curd = cheb(sx, sy, tx, ty)
        gain = curd - dtarget
        dop = cheb(nx, ny, ox, oy)
        val = gain * 1000 + dop - (dtarget * 3)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]