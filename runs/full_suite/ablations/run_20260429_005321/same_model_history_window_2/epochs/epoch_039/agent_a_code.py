def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    if not resources:
        tx, ty = (w // 2), (h // 2)
        best = (0, 0)
        best_sc = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sc = -cheb(nx, ny, tx, ty) - 0.25 * cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc, best = sc, (dx, dy)
        return [best[0], best[1]]

    # Strategic change: pick moves that (1) create a win race on some resource (you earlier),
    # else (2) maximize progress while staying relatively farther from opponent.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist_me = 0
        dist_op = 0
        # Evaluate best target resource under this move
        local_best = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # If you are not ahead, penalize; if ahead, reward strongly.
            ahead = d_op - d_me  # positive means you get there sooner or equal
            # Also prefer resources that are closer overall (fewer remaining steps).
            closeness = -0.15 * (d_me + d_op)
            # Avoid moving into immediate "opponent grabs" zones: discourage moves that reduce margin.
            margin_score = 6.0 * ahead - 0.45 * (d_me)
            sc = margin_score + closeness
            if sc > local_best:
                local_best = sc

        # Additional tie-breaker: keep distance from opponent to reduce contest swapping.
        dist_me = cheb(nx, ny, ox, oy)
        tie = 0.08 * dist_me
        total = local_best + tie

        if total > best_score:
            best_score = total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]