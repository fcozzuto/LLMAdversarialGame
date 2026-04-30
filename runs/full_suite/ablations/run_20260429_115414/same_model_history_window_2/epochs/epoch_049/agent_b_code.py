def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d_op = cheb(nx, ny, ox, oy)
            d_ctr = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
            sc = d_op * 2 + (-d_ctr)
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best_sc = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_me_op = cheb(nx, ny, ox, oy)
        # Evaluate by best resource for us under "race" distance advantage.
        local_best = -10**18
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # Prefer being closer than opponent; tie-break by shorter personal distance and farther from opponent.
            adv = d2 - d1
            sc = adv * 50 - d1 * 3 + d_me_op * 0.8
            if sc > local_best:
                local_best = sc
        # If we have no meaningful advantage, still prefer reducing our closest distance.
        if local_best < -10**17:
            local_best = -cheb(nx, ny, resources[0][0], resources[0][1])
        # Slightly bias moves that reduce distance to the currently closest resource.
        close_d = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        sc_total = local_best + (-close_d) * 1.5
        if sc_total > best_sc:
            best_sc = sc_total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]