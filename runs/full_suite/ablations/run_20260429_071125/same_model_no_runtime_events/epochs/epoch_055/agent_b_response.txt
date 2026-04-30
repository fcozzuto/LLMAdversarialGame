def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    if not resources:
        # Fall back: keep distance while improving mobility away from opponent.
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            val = cheb(nx, ny, ox, oy)  # maximize
            if best is None or val > best[0] or (val == best[0] and (dx, dy) < best[1]):
                best = (val, (dx, dy))
        return list(best[1])

    # Choose a target resource where we have maximum distance advantage vs opponent.
    best_t = None
    best_adv = None
    best_d_self = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds
        if best_t is None or adv > best_adv or (adv == best_adv and ds < best_d_self):
            best_t = (tx, ty)
            best_adv = adv
            best_d_self = ds

    tx, ty = best_t

    # Move that maximizes our advantage after the move (opponent assumed stationary this turn).
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds2 = cheb(nx, ny, tx, ty)
        adv2 = cheb(ox, oy, tx, ty) - ds2
        tie = (abs(nx - tx) + abs(ny - ty)) + 0.001 * (dx * dx + dy * dy)
        if best is None or adv2 > best[0] or (adv2 == best[0] and tie < best[1]):
            best = (adv2, tie, (dx, dy))
    return [best[2][0], best[2][1]]