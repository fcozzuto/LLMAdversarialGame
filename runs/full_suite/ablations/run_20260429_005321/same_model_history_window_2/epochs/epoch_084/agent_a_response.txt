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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = ox, oy
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dme = cheb(nx, ny, tx, ty)
            dop = cheb(nx, ny, ox, oy)
            key = (dme, -dop, nx, ny)
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return list(best if best is not None else [0, 0])

    best_res = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; if tied, prefer those where opponent is far.
        key = (d_me - d_op, d_me, -d_op, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_res = key, (rx, ry)

    rx, ry = best_res
    best = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me = cheb(nx, ny, rx, ry)
        d_op_next = cheb(nx, ny, ox, oy)
        # Move closer to target, but also avoid giving opponent a better capture position.
        # We approximate by maximizing opponent distance from our next position and resources.
        d_op_to_target = cheb(ox, oy, rx, ry)
        key = (d_me, -d_op_next, d_op_to_target, nx, ny)
        if best_key is None or key < best_key:
            best_key, best = key, (dx, dy)

    return [int(best[0]), int(best[1])]