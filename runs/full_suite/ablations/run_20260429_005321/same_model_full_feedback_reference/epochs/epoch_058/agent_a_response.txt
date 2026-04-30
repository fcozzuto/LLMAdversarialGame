def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy)  # squared Euclid

    def best_resource_score(x, y):
        if not resources:
            return -10**18
        my_best = -10**18
        for rx, ry in resources:
            dmy = cheb(x, y, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # Prefer resources I can reach no later (dmy <= dop), otherwise contest.
            ahead = dop - dmy
            s = 1000000 * (1 if dmy <= dop else 0) + ahead
            # Slightly prefer closer targets once contention is decided.
            s -= dmy * 0.001
            if s > my_best:
                my_best = s
        return my_best

    # Immediate move evaluation: maximize advantage toward good resources.
    best = (-10**30, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Also discourage drifting away from opponent too much if I can't secure a resource.
        sres = best_resource_score(nx, ny)
        d2op = cheb(nx, ny, ox, oy)
        center_bias = -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)
        s = sres + 0.0005 * d2op + 0.01 * center_bias
        if s > best[0]:
            best = (s, dx, dy)

    return [int(best[1]), int(best[2])]