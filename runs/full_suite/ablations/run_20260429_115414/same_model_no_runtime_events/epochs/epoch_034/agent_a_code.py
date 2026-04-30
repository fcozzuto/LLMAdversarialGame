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
    if not resources:
        return [0, 0]

    try:
        rem = int(observation.get("remaining_resource_count"))
    except:
        rem = len(resources)
    late = rem <= 4

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_pen(x, y):
        p = 0
        for (bx, by) in obstacles:
            if cheb(x, y, bx, by) <= 1:
                p += 2
        return p

    targets = resources
    if late:
        targets = sorted(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))[:4]
    else:
        targets = resources

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)
        p_obs = obs_pen(nx, ny)

        d_t = 10**9
        for tx, ty in targets:
            d = cheb(nx, ny, tx, ty)
            if d < d_t:
                d_t = d

        d_from_self = cheb(nx, ny, sx, sy)
        alpha = 3.2 if late else 2.4
        beta = 1.0 if late else 0.6
        gamma = 0.7 if late else 0.5
        delta = 0.15 * (1 if (dx == 0 and dy == 0) else 0)

        score = (-alpha * d_t) + (beta * d_op) - (gamma * p_obs) - delta - 0.05 * d_from_self
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]