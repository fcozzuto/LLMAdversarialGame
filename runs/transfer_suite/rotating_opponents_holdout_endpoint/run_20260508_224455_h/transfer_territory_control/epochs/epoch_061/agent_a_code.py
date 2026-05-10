def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(lst):
        s = set()
        for c in lst or []:
            try:
                s.add((int(c[0]), int(c[1])))
            except:
                pass
        return s

    obstacles = to_set(observation.get("obstacles"))
    myt = to_set(observation.get("self_territory"))
    opt = to_set(observation.get("opponent_territory"))
    un = to_set(observation.get("unclaimed_cells"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    my_adj = set()
    for (x, y) in myt:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in un:
                my_adj.add((nx, ny))
    targets = my_adj if my_adj else (un if un else (opt if opt else set()))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = [0, 0]
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            sc = -10**12
        else:
            cell = (nx, ny)
            # Prefer expanding into our frontier, otherwise sweep near opponent.
            if cell in myt:
                near = 0
            elif targets:
                near = -min(dist(cell, t) for t in targets)
            else:
                near = -dist(cell, (ox, oy))
            # Territory flip incentives
            steal = 0
            if cell in opt:
                steal = 120
            # Slightly keep distance from opponent if we can't steal
            avoid = 0 if cell in opt else -0.8 * dist(cell, (ox, oy))
            # Center bias to reduce edge stalling
            center = -0.02 * ((nx - (w - 1) / 2) ** 2 + (ny - (h - 1) / 2) ** 2)
            sc = near + steal + avoid + center
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return [int(best[0]), int(best[1])]