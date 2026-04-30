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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        best = (10**9, None)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if not ok(nx, ny):
                    continue
                d = cheb(nx, ny, tx, ty)
                if d < best[0]:
                    best = (d, (dx, dy))
        return best[1] if best[1] is not None else [0, 0]

    if resources:
        tx, ty = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
        move = step_toward(tx, ty)
        if move != [0, 0]:
            return [int(move[0]), int(move[1])]

    mx = 0
    my = 0
    best = (10**9, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[1])):
                best = (d, dx)
                mx, my = dx, dy
    return [int(mx), int(my)]