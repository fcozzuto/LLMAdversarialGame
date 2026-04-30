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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    target = (ox, oy)
    if resources:
        best = resources[0]
        bd = dist(best[0], best[1], ox, oy)
        for r in resources[1:]:
            d = dist(r[0], r[1], sx, sy)
            if d < bd:
                bd = d
                best = r
        target = best

    tx, ty = target
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        s = -(dist(nx, ny, tx, ty))
        if resources and (nx, ny) == resources[0]:
            s += 1000
        if (nx, ny) == (tx, ty):
            s += 200
        # slight tie-break: prefer moves that reduce distance to opponent
        s -= 0.01 * dist(nx, ny, ox, oy)
        if s > best_score:
            best_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]