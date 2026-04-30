def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Value = how much closer we are than opponent (contest/deny), with secondary distance shaping.
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer large (opd - myd). If tied, prefer closer absolute distance to us.
        # Add tiny deterministic bias towards nearer-by coordinates.
        key = (opd - myd, -(myd), -(rx + ry * 7))
        if best is None or key > best[0]:
            best = (key, rx, ry)
    rx, ry = best[1], best[2]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_step = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = cheb(nx, ny, rx, ry)
        d_op_to = cheb(nx, ny, ox, oy)
        # Encourage approaching target, discourage giving opponent too much space near our path.
        score = (-d_to, -((d_op_to + (d_to // 2)) // 2), 0 if dx == 0 and dy == 0 else -1, -(nx * 9 + ny))
        if best_score is None or score > best_score:
            best_score = score
            best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    dx, dy = best_step
    return [int(dx), int(dy)]