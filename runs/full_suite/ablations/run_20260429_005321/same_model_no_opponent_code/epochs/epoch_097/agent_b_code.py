def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx = w // 2
        ty = h // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if (d, nx, ny, dx) < (best[0], best[1], best[2], best[3]):
                best = (d, nx, ny, dx)
        return [int(best[3] if best[3] is not None else 0), int(best[2] - best[2] + 0)]  # ensure ints

    best_target = None
    best_score = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer targets we can reach earlier; slight tie-break toward closeness.
        score = (opd - myd, -myd, rx, ry)
        if best_score is None or score > best_score:
            best_score = score
            best_target = (rx, ry)

    rx, ry = best_target
    curd = cheb(sx, sy, rx, ry)
    best_move = (curd, 10**9, 10**9, 0, 0)  # (dist, nx, ny, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, rx, ry)
        # Primary: reduce distance; Secondary: move toward target deterministically; Tertiary: prefer staying less.
        if (nd, nx, ny, dx, dy) < (best_move[0], best_move[1], best_move[2], best_move[3], best_move[4]):
            best_move = (nd, nx, ny, dx, dy)

    return [int(best_move[3]), int(best_move[4])]