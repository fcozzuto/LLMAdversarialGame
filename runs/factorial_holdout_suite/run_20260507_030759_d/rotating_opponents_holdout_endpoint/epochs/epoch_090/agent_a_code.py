def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and ok(x, y):
                targets.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best = None
    bestv = None

    if targets:
        tx, ty = min(targets, key=lambda t: (cheb(sx, sy, t[0], t[1]), (t[0], t[1])))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if best is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = cheb(nx, ny, ox, oy)
        if best is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]