def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    tx, ty = None, None
    if resources:
        bestv = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer nearer resources, but also prefer those where opponent is farther.
            v = ds - 0.6 * do
            if bestv is None or v < bestv or (v == bestv and (rx, ry) < (tx, ty)):
                bestv = v
                tx, ty = rx, ry
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose best next step that moves closer to target; if multiple, bias away from opponent.
    best = None
    best_step = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dnt = dist(nx, ny, tx, ty)
        dno = dist(nx, ny, ox, oy)
        # Primary: reduce distance to target. Secondary: keep distance from opponent.
        key = (dnt, -dno, dx, dy)
        if best is None or key < best:
            best = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]