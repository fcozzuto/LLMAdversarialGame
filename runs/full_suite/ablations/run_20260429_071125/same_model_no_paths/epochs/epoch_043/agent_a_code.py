def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    def man(ax, ay, bx, by):
        ax -= bx
        if ax < 0:
            ax = -ax
        ay -= by
        if ay < 0:
            ay = -ay
        return ax + ay

    target = None
    bestd = 10**18
    for x, y in resources:
        d = man(sx, sy, x, y)
        if d < bestd:
            bestd = d
            target = (x, y)

    if target is None:
        target = (ox, oy)

    tx, ty = target
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    bestscore = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        score = d * 10 + (0 if (nx, ny) == (tx, ty) else 1)
        if score < bestscore:
            bestscore = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]