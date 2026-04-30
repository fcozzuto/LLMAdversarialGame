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
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9
    best_tie = 10**9

    # Deterministic target selection: try to maximize "advantage" over opponent toward the best resource.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
        my_best = -10**9
        my_best_myd = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # higher means I'm closer or opponent is farther
            if adv > my_best or (adv == my_best and (myd < my_best_myd or (myd == my_best_myd and (rx + ry) < 0))):
                my_best = adv
                my_best_myd = myd
        # Tie-break: prefer smaller my_best_myd, then lexicographically smaller move.
        score = my_best
        tie = my_best_myd
        if score > best_score or (score == best_score and (tie < best_tie or (tie == best_tie and (dxm, dym) < best_move))):
            best_score = score
            best_tie = tie
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]