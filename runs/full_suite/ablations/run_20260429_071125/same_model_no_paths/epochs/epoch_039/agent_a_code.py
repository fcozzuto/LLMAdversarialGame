def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**9)

    moves = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    if not resources:
        # deterministic fallback: drift toward the center
        tx, ty = w // 2, h // 2
        bestm = None
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # Strategic change: pick the move that maximizes relative closeness to the best available resource.
    # Score compares (opponent distance - self distance) with a slight tie-break for speed.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        rel_best = -10**9
        self_best = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            rel = (do - ds)  # positive means we are closer than opponent
            if rel > rel_best:
                rel_best = rel
                self_best = ds
            elif rel == rel_best and ds < self_best:
                self_best = ds
        # Encourage moving toward a resource that we can realistically reach first; discourage suicidal moves
        # by also including our absolute distance as mild penalty.
        score = rel_best * 100 - self_best
        if score > best[1]:
            best = ((dx, dy), score)

    return [int(best[0][0]), int(best[0][1])]