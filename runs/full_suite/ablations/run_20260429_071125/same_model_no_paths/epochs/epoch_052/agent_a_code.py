def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
    if not free(sx, sy):
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if resources:
        resources.sort(key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))
        tx, ty = resources[0]
    else:
        tx, ty = ox, oy

    best = (10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best[0] or (d == best[0] and (dx, dy) < best[1]):
            best = (d, (dx, dy))
    dx, dy = best[1] if best[1] is not None else (0, 0)
    return [dx, dy]