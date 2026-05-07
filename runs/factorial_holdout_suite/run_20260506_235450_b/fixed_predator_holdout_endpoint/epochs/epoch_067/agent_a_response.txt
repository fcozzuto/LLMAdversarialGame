def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    res_list = [tuple(r) for r in resources if len(r) >= 2 and inb(r[0], r[1])]
    if not res_list:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(px, py):
        best = None
        bestv = None
        for tx, ty in res_list:
            if (tx, ty) in obstacles:
                continue
            myd = cheb(px, py, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Strongly prefer targets where we are at least as close as opponent.
            v = (opd - myd) * 30 - myd
            # Deterministic tie-break: lexicographic by target coords.
            key = (v, -tx, -ty)
            if bestv is None or key > (bestv[0], bestv[1], bestv[2]):
                bestv = (v, -tx, -ty)
                best = (tx, ty)
        return best

    if (sx, sy) in obstacles:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    if (sx, sy) in res_list:
        return [0, 0]

    tx, ty = best_target(sx, sy)
    if tx is None:
        return [0, 0]

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # If opponent is closer, try to reduce our gap more aggressively.
        gap = opd - myd
        # Bonus if move would land on a resource cell.
        bonus = 60 if (nx, ny) in set(res_list) else 0
        score = gap * 20 - myd + bonus
        # Deterministic tie-break: prefer smallest |dx|+|dy|, then lexicographic.
        dist = abs(dx) + abs(dy)
        key = (score, -dist, -dx, -dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]