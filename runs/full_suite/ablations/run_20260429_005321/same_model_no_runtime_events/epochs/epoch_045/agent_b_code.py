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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (0, 0), (1, 1), (1, -1), (-1, 1)]

    if not resources:
        tx, ty = ox, oy
        best = (10**9, None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, (dx, dy))
        dx, dy = best[1] if best[1] is not None else (0, 0)
        return [dx, dy]

    bestv = 10**18
    bestm = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        bestt = None
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            v = ds + 2 * (0 if do > ds else (ds - do))  # prefer resources closer than opponent
            if bestt is None or v < bestt:
                bestt = v
        if bestt is None:
            continue
        if bestt < bestv:
            bestv = bestt
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]