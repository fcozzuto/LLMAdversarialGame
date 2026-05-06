def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        bx = 0
        by = 0
        if sx < tx: bx = 1
        elif sx > tx: bx = -1
        if sy < ty: by = 1
        elif sy > ty: by = -1
        return [bx, by]

    # Evaluate best move by improving "advantage" on a target resource.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Tie-breaker also considers staying closer to opponent when leads are small.
        my_best = 10**9
        opp_best = 10**9
        adv_best = -10**9
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if dm < my_best: my_best = dm
            if do < opp_best: opp_best = do
            adv = (do - dm)  # positive means we are closer to this resource
            if adv > adv_best: adv_best = adv

        # Prefer taking a resource we can reach earlier; otherwise minimize our distance.
        val = 0.0
        val += 5.0 * adv_best
        val += -1.2 * my_best
        val += 0.25 * opp_best

        # Small deterministic preference for not moving wildly toward edges late in game.
        edge_pen = abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2)
        val += -0.03 * edge_pen

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move