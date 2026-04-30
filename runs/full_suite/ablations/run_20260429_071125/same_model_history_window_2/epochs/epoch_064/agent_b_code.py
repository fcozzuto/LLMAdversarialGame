def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
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

    tx, ty = w // 2, h // 2
    if resources:
        best = None
        best_rel = -10**9
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            rel = opd - myd
            key = (rel, -myd, -rx, -ry)
            if rel > best_rel or (rel == best_rel and (best is None or key > best)):
                best_rel = rel
                best = (rx, ry)
        if best is not None:
            # If we aren't "winning" a resource, switch to a contest point.
            if best_rel <= 0:
                tx, ty = w // 2, h // 2
            else:
                tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_dist = 10**9

    # Prefer moves that bring us closer to (tx,ty) while not walking into obstacles.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_dist or (d == best_dist and (dx, dy) < best_move):
            best_dist = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]