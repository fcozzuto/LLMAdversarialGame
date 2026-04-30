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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Choose a resource where we have the greatest deterministic "race" advantage.
    chosen = None
    best_adv = None
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer (or opponent farther)
            key = (adv, -ds, -(rx + ry), rx, ry)
            if chosen is None or key > (best_adv,):
                chosen = (rx, ry)
                best_adv = key[0]
        # If all are negative, fall back to closest with deterministic tie-break.
        if best_adv < 0:
            best = None
            for rx, ry in resources:
                ds = cheb(sx, sy, rx, ry)
                key = (-ds, -(rx + ry), rx, ry)
                if best is None or key > best[0]:
                    best = (key, (rx, ry))
            chosen = best[1]
    else:
        chosen = (ox, oy)

    rx, ry = chosen
    # Score each move: maximize reduction toward chosen resource; break ties by increasing separation from opponent.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        ds_before = cheb(sx, sy, rx, ry)
        ds_after = cheb(nx, ny, rx, ry)
        do_before = cheb(ox, oy, rx, ry)
        do_after = cheb(ox, oy, rx, ry)  # opponent doesn't move now; keep stable for determinism

        opp_sep_before = cheb(sx, sy, ox, oy)
        opp_sep_after = cheb(nx, ny, ox, oy)

        advantage_before = do_before - ds_before
        advantage_after = do_after - ds_after

        score = (advantage_after, -(ds_after), opp_sep_after, dx, dy)
        if best_move is None or score > best_score:
            best_move = (dx, dy)
            best_score = score

    return [int(best_move[0]), int(best_move[1])]