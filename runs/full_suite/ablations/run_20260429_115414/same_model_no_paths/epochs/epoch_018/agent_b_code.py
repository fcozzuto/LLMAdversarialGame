def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
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

    if not resources:
        # No resources: keep pressure by moving to reduce opponent-chebyshev distance
        best = (10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = cheb(nx, ny, ox, oy)
            # deterministic tie-break: prefer staying still
            if (score, dx == 0 and dy == 0) < (best[0], best[1] == 0 and best[2] == 0):
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Pick best target based on advantage: (opponent distance - my distance)
    best_t = resources[0]
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd
        # Prefer higher adv, then closer target, then deterministic by coordinates
        key = (adv, -myd, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Encourage reaching target, but also block opponent by increasing their effective advantage gap
        adv2 = opd2 - myd2
        # Small penalty for increasing distance to resources overall (keeps motion stable)
        min_other = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < min_other:
                min_other = d
        score = adv2 * 1000 - myd2 * 10 - min_other
        # deterministic tie-break: prefer (0,0), then lexicographically smallest (dx,dy)
        tie = (score, dx == 0 and dy == 0, -dx, -dy)
        cur = (best[0], best[1] == 0 and best[2] == 0, -best[1], -best[2])
        if tie > cur:
            best = (score, dx, dy)

    return [best[1], best[2]]