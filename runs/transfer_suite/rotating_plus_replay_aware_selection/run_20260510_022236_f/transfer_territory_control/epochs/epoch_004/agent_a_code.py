def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_xy_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    s.add((int(p[0]), int(p[1])))
                except:
                    pass
        return s

    obs = to_xy_set(observation.get("obstacles"))
    res = to_xy_set(observation.get("resources"))
    un = to_xy_set(observation.get("unclaimed_cells", observation.get("unclaimed")))
    st = to_xy_set(observation.get("self_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mindist(x, y, S):
        d = 10**9
        for a, b in S:
            dd = abs(a - x) + abs(b - y)
            if dd < d:
                d = dd
        return d if d != 10**9 else 0

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sc = 0
        if (nx, ny) in res:
            sc += 1000
        elif (nx, ny) in un:
            sc += 80
        elif (nx, ny) in st:
            sc += 20
        dres = mindist(nx, ny, res) if res else 0
        if res:
            sc += -2 * dres
        dun = mindist(nx, ny, un) if un else 0
        if un:
            sc += -0.5 * dun
        dop = abs(nx - ox) + abs(ny - oy)
        sc += min(40, dop)
        if dop <= 2:
            sc -= 100
        if best is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]