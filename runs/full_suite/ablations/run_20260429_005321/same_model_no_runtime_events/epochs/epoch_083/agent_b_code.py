def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        target = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0] * 10 + r[1]))
        tx, ty = target
        txo = cheb(tx, ty, ox, oy)
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        txo = 0

    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dres = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)

        # Score: prefer smaller distance to resource/center; keep away from opponent;
        # also slightly prefer staying on the "progress" side toward target.
        prog = (cheb(sx, sy, tx, ty) - dres)
        # When target is potentially contested, weigh opponent proximity more.
        contest = 1 if resources and cheb(sx, sy, tx, ty) >= txo else 0
        v = (dres * 1000) - (dop * (3 + contest * 2)) - (prog * 10) + (0 if (nx, ny) == (tx, ty) else 0)

        if bestv is None or v < bestv:
            bestv = v
            best = (dx, dy)
        elif v == bestv and best is not None:
            # Deterministic tie-break: fixed dir order
            if dirs.index((dx, dy)) < dirs.index(best):
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]