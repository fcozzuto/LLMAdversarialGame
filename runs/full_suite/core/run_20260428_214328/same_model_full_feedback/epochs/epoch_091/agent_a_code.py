def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        best, bv = [0, 0], 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bv:
                bv = d
                best = [dx, dy]
        return best

    # Pick promising targets where I'm relatively closer than opponent (deterministic tie-break)
    scored = []
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        scored.append(((md - od), md, od, rx, ry))
    scored.sort()
    candidates = [(x, y) for _, _, _, x, y in scored[:min(5, len(scored))]]

    # Evaluate each possible move by improving my distance to best candidate while keeping opponent far
    best_move, best_val = [0, 0], -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # If move is blocked, staying will also be considered elsewhere; here skip invalid.
        local_best = -10**18
        for rx, ry in candidates:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer: smaller myd, larger separation opd-myd. Small bonus if closer than current.
            val = (opd - myd) * 100 - myd * 3
            local_best = val if val > local_best else local_best
        # Mild preference for moving away from opponent if tied
        tie_b = cheb(nx, ny, ox, oy)
        val2 = local_best * 1000 - tie_b
        if val2 > best_val:
            best_val = val2
            best_move = [dx, dy]

    return best_move