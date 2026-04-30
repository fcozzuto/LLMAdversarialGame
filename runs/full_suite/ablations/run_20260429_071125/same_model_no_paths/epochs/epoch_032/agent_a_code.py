def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    def metric(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = [0, 0]
    best_val = -10**9

    target = None
    if resources:
        bestd = 10**9
        for x, y in resources:
            d = metric(sx, sy, x, y)
            if d < bestd:
                bestd = d
                target = (x, y)
        tx, ty = target
    else:
        tx, ty = ox, oy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            d_to = metric(nx, ny, tx, ty)
            d_op = metric(nx, ny, ox, oy)
            val = (-d_to * 10) + (d_op)  # reach resources, keep distance from opponent
        else:
            d_op = metric(nx, ny, ox, oy)
            val = d_op  # no resources: maximize distance
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best