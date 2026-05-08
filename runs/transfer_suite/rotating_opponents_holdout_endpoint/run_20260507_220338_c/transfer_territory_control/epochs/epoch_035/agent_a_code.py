def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w); h = int(h)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    resources = []
    for p in (observation.get("resources") or []):
        try:
            resources.append((int(p[0]), int(p[1])))
        except:
            pass

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        try:
            unclaimed.add((int(p[0]), int(p[1])))
        except:
            pass

    tx = None; ty = None
    best_r = None
    for (x, y) in resources:
        d = abs(x - sx) + abs(y - sy)
        if best_r is None or d < best_r:
            best_r = d; tx = x; ty = y

    best_u = None; ux = None; uy = None
    if unclaimed:
        for (x, y) in unclaimed:
            d = abs(x - sx) + abs(y - sy)
            if best_u is None or d < best_u:
                best_u = d; ux = x; uy = y

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles

    def score(x, y):
        s = 0
        if resources:
            s += -10 * (abs(x - tx) + abs(y - ty))
            if (x, y) == (tx, ty): s += 1000
        elif unclaimed:
            s += -8 * (abs(x - ux) + abs(y - uy))
            if (x, y) in unclaimed: s += 200
        s += -4 * (abs(x - ox) + abs(y - oy))
        return s

    best = None; best_mv = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny): 
            continue
        sc = score(nx, ny)
        if best is None or sc > best or (sc == best and (dx, dy) < best_mv):
            best = sc; best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]