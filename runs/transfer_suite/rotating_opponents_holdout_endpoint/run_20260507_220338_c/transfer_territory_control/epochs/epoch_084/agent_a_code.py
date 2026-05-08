def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    selfT = set(tuple(t) for t in (observation.get("self_territory") or []))
    oppT = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))

    res = observation.get("resources") or []
    res_cells = []
    for p in res:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res_cells.append((x, y))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(x, y):
        if (x, y) in blocked:
            return -10**9
        s = 0
        if (x, y) in unclaimed:
            s += 400
        if (x, y) in selfT:
            s += 80
        if (x, y) in oppT:
            s -= 200
        if (x, y) == (ox, oy):
            s -= 500
        d = abs(x - ox) + abs(y - oy)
        s -= (8 - min(8, d)) * 15
        if res_cells:
            mr = min(abs(x - rx) + abs(y - ry) for rx, ry in res_cells)
            s += 200 - min(200, mr * 20)
        return s

    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            sc = cell_score(nx, ny)
            if sc > best_s:
                best_s = sc
                best = (dx, dy)
    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]