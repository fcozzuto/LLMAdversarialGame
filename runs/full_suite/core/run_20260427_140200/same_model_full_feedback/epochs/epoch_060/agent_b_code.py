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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if cheb(sx, sy, ox, oy) <= 1:
        best_move = (0, 0)
        best = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best:
                best = d
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    if resources:
        # Pre-rank targets by "reach advantage" from current position.
        ranked = []
        for rx, ry in resources:
            dm = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            ranked.append((dm - 0.85 * do, dm, rx, ry))
        ranked.sort()
        # Consider up to 5 best targets for speed/determinism.
        targets = [(t[2], t[3]) for t in ranked[:5]]
    else:
        targets = [(w // 2, h // 2)]

    best_move = (0, 0)
    best_val = 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Move evaluation: reduce distance to best reachable target with opponent-pressure term.
        val = 10**18
        for rx, ry in targets:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Also mildly discourage stepping closer to opponent.
            opp_closer_pen = 0.08 * cheb(nx, ny, ox, oy)
            cand = myd - 0.75 * opd + opp_closer_pen
            if cand < val:
                val = cand
        # Slight preference for progress if equal.
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]