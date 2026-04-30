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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def score_adv(x, y):
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer resources we can reach sooner than opponent; tie-break by closer to us.
        return (sd - od, sd, x, y)

    tx, ty = None, None
    if resources:
        resources.sort()
        best = None
        for x, y in resources:
            cand = score_adv(x, y)
            if best is None or cand < best:
                best = cand
                tx, ty = x, y
    else:
        # No resources visible: move toward center.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_tuple = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: keep away from opponent; Tertiary: deterministic order.
        cand = (d_to, -d_op, dx, dy)
        if best_tuple is None or cand < best_tuple:
            best_tuple = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]