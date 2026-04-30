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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; tie-break by absolute speed and location toward mid
            key = ((do - ds), (-ds), (abs(rx - w // 2) + abs(ry - h // 2)))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: bias toward center-corner that keeps pressure
        if cheb(sx, sy, 0, h - 1) <= cheb(sx, sy, w - 1, 0):
            tx, ty = 0, h - 1
        else:
            tx, ty = w - 1, 0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # If we are closer than opponent, prioritize; otherwise, deny by moving to reduce gap.
        sc = (opp_d - my_d) * 100 - my_d
        # Mild obstacle-avoidance surrogate: prefer moves that have more legal neighbors
        neigh = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if ok(ax, ay):
                neigh += 1
        sc += neigh
        # Slightly prefer not moving away from center (keeps consistent trajectories)
        sc -= (abs(nx - w // 2) + abs(ny - h // 2)) // 4
        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]