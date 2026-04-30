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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    tx, ty = (w - 1, h - 1)
    if resources:
        best = None
        for (rx, ry) in resources:
            d = cheb(sx, sy, rx, ry)
            md = abs(sx - rx) + abs(sy - ry)
            key = (d, md, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    best_move = (None, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist_to_target = cheb(nx, ny, tx, ty)
        dist_to_opp = cheb(nx, ny, ox, oy)
        on_resource = 1 if (nx, ny) in set(resources) else 0
        score = (-dist_to_target) + 0.35 * dist_to_opp + 2.0 * on_resource
        key = (score, -dx, -dy)
        if best_move[0] is None or key[0] > best_move[1] or (key[0] == best_move[1] and (dx, dy) < best_move[0]):
            best_move = ((dx, dy), key[0])

    if best_move[0] is None:
        return [0, 0]
    dx, dy = best_move[0]
    return [dx, dy]