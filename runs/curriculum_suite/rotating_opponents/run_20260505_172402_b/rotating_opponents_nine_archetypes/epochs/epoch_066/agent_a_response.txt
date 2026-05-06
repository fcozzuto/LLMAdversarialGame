def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if best is None:
            best = (rx, ry)
            best_key = (-1.0e9, 0, 0, rx, ry)
        # Prefer self closer than opponent; then closer; then tie-break by coordinates
        key = (-(do - ds), -ds, -(abs(rx - sx) + abs(ry - sy)), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    direct = []
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    direct.append((dx, dy))
    if dx != 0 and dy != 0:
        direct.append((dx, 0))
        direct.append((0, dy))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Try direct-ish steps first
    for ddx, ddy in direct:
        nx, ny = sx + ddx, sy + ddy
        if valid(nx, ny) and (ddx != 0 or ddy != 0 or (nx, ny) == (sx, sy)):
            return [ddx, ddy]

    # Otherwise choose move that minimizes distance to target, with deterministic tie-break
    curd = cheb(sx, sy, tx, ty)
    bestm = (0, 0)
    bestd = curd
    best_t = (0, 0)
    for ddx, ddy in moves:
        if ddx == 0 and ddy == 0:
            nx, ny = sx, sy
        else:
            nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        t = (abs(ddx), abs(ddy), ddx, ddy)
        if d < bestd or (d == bestd and t < best_t):
            bestd = d
            bestm = (ddx, ddy)
            best_t = t

    return [int(bestm[0]), int(bestm[1])]