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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    best = None
    contest = []

    for rx, ry in resources:
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        if our_d <= opp_d:
            contest.append((our_d, -opp_d, rx, ry))
    if contest:
        contest.sort()
        d1, negd2, rx, ry = contest[0]
        target = (rx, ry)
    else:
        # If we can't contest, go for the opponent-closest resource to reduce their lead.
        for rx, ry in resources:
            our_d = cheb(sx, sy, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            key = (opp_d, our_d, rx, ry)
            if best is None or key < best:
                best = key
                target = (rx, ry)

    if target is None:
        tx, ty = (w // 2), (h // 2)
    else:
        tx, ty = target

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_t_cur = cheb(sx, sy, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer moves that reduce distance to target; then maximize opponent distance; then deterministic tie-break.
        val = (-(d_to_t - d_to_t_cur), d_to_t, -d_opp, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]