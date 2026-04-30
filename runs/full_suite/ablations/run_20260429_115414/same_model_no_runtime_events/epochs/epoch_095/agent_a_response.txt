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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort()

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        best_score = -10**18
        for (rx, ry) in sorted(resources):
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            score = opd - myd
            if (score > best_score) or (score == best_score and (myd < best[0] or (myd == best[0] and (rx, ry) < best[1]))):
                best_score = score
                best = (myd, (rx, ry))
        tx, ty = best[1]

    curd = cheb(sx, sy, tx, ty)
    chosen = None
    chosen_dist = 10**18
    chosen_lex = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        if nd < chosen_dist or (nd == chosen_dist and (dx, dy) < chosen_lex):
            chosen_dist = nd
            chosen = (dx, dy)
            chosen_lex = (dx, dy)

    if chosen is None:
        return [0, 0]

    return [int(chosen[0]), int(chosen[1])]