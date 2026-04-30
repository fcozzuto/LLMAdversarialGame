def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        best_sc = -10**9
        for dx, dy, nx, ny in moves:
            sc = cheb(nx, ny, ox, oy)
            if best is None or sc > best_sc or (sc == best_sc and (dx, dy) < (best[0], best[1])):
                best_sc = sc
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best = None
    best_sc = -10**18
    for dx, dy, nx, ny in moves:
        # Score: how much closer we are than opponent to the best resource; tie-break by staying not too close to opponent.
        best_res = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            # Prefer resources where opponent is relatively far; small penalty when we get too close to opponent.
            sc = adv * 10 + (do - cheb(nx, ny, ox, oy))
            if sc > best_res:
                best_res = sc
        # Slight deterministic tie-break: prefer moves that keep us moving toward the "current" closest resource.
        cur_closest = 10**9
        tx, ty = resources[0]
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < cur_closest:
                cur_closest = d
                tx, ty = rx, ry
        dnew = cheb(nx, ny, tx, ty)
        sc_total = best_res * 100 - dnew
        if best is None or sc_total > best_sc or (sc_total == best_sc and (dx, dy) < (best[0], best[1])):
            best_sc = sc_total
            best = (dx, dy)

    return [int(best[0]), int(best[1])]