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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) != (sx, sy) and free(x, y):
                resources.append((x, y))

    if resources:
        rx, ry = min(resources, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        rx, ry = w // 2, h // 2

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dres = abs(nx - rx) + abs(ny - ry)
        dopp = abs(nx - ox) + abs(ny - oy)
        sc = -dres + 0.35 * dopp
        if resources and (nx, ny) in set(resources):
            sc += 10000
        if best is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]