def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs and 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    if resources:
        cx = sum(x for x, _ in resources) / len(resources)
        cy = sum(y for _, y in resources) / len(resources)
        target = (cx, cy)
    else:
        target = ((w - 1) / 2.0, (h - 1) / 2.0)

    def score(nx, ny):
        tx, ty = target
        dx1 = nx - tx
        dy1 = ny - ty
        dres = dx1 * dx1 + dy1 * dy1
        dopp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        return dres - 0.1 * dopp

    best = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            sc = score(nx, ny)
            if best is None or sc < best or (sc == best and (dx, dy) < best_move):
                best = sc
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]