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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort()

    if resources:
        best_t = resources[0]
        best_v = 10**18
        for tx, ty in resources:
            d_me = cheb(sx, sy, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # Favor targets closer to us than opponent; also prefer reasonably near overall.
            v = d_me - 0.55 * d_op + 0.07 * (cheb(tx, ty, (w - 1) // 2, (h - 1) // 2))
            if v < best_v:
                best_v = v
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = (0, 0)
    best_score = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # Tightest distance to target, but keep away from opponent to avoid contest flips.
        score = d_me - 0.35 * d_op
        if score < best_score:
            best_score = score
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]