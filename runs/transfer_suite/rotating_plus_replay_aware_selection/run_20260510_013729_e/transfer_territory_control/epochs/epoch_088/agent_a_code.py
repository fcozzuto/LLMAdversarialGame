def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                targets.append((x, y))
    res = observation.get("resources") or []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                targets.append((x, y))
    if not targets:
        opps = observation.get("opponent_territory") or []
        for p in opps:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    targets.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best = None
    if targets:
        def dist(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        tx, ty = min(targets, key=lambda t: (dist((sx, sy), t), t[0], t[1]))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) == (sx, sy):
                sc = -10**9 + abs(nx - ox) + abs(ny - oy)
            else:
                sc = -dist((nx, ny), (tx, ty)) + 2 * dist((nx, ny), (ox, oy))
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        if best:
            return [int(best[1]), int(best[2])]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) == (sx, sy):
            continue
        sc = 0
        if abs(nx - ox) + abs(ny - oy) > abs(sx - ox) + abs(sy - oy):
            sc += 2
        if nx == w // 2 and ny == h // 2:
            sc += 1
        sc += -(abs(nx - sx) + abs(ny - sy)) * 0
        if best is None or sc > best[0]:
            best = (sc, dx, dy)
    if best:
        return [int(best[1]), int(best[2])]
    return [0, 0]