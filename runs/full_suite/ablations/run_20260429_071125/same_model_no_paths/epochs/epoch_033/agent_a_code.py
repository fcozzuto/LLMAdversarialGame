def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Target selection: pick resource where we have an advantage in time-to-reach.
    # Prefer resources that are closer to us than to the opponent; otherwise, contest nearest.
    target = None
    best_t = None
    best_rank = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Advantage: positive if we are closer or equal
        adv = do - ds
        # Also consider absolute distance so we don't chase far-away leads
        rank = adv * 100 - ds
        if best_t is None or rank > best_rank or (rank == best_rank and (ds < cheb(sx, sy, best_t[0], best_t[1]))):
            best_t = (rx, ry)
            best_rank = rank

    if target is None:
        return [0, 0]
    tx, ty = target

    # Choose move that minimizes our distance to target, but breaks ties by improving advantage vs opponent.
    best = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        adv2 = do2 - ds2
        # Prefer reaching/approaching target; if equal, prefer increasing advantage; then prefer reducing absolute distance
        val = -ds2 * 1000 + adv2 * 10
        if val > best_val or (val == best_val and (ds2 < cheb(sx, sy, tx, ty))):
            best_val = val
            best = [dx, dy]

    return best