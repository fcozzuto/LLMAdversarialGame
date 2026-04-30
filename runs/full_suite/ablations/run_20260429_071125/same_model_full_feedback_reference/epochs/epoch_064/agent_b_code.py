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
    resources.sort()

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best_res = None
        best_ahead = -10**18
        best_break = 10**18
        for rx, ry in resources:
            ds0 = cheb(sx, sy, rx, ry)
            do0 = cheb(ox, oy, rx, ry)
            ahead = do0 - ds0  # positive means we are closer/equal
            if ahead > best_ahead or (ahead == best_ahead and ds0 < best_break):
                best_ahead = ahead
                best_break = ds0
                best_res = (rx, ry)
        rx, ry = best_res
    else:
        rx = ry = None

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        if resources and (nx, ny) == (rx, ry):
            val = 10**9
        else:
            if resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                val = -ds + 0.65 * do
            else:
                ds = cheb(nx, ny, ox, oy)
                val = -ds
            # keep some separation and avoid oscillation bias near opponent
            dso = cheb(nx, ny, ox, oy)
            val -= 0.08 * dso
            # deterministic tie-break using coordinates
            val -= 1e-6 * (abs(nx - sx) + 2 * abs(ny - sy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]