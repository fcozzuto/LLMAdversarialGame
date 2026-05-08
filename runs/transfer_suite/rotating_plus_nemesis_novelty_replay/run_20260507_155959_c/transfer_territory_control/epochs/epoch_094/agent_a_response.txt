def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    edge_dist = lambda x, y: min(x, y, w - 1 - x, h - 1 - y)

    opp_list = list(opp_t)
    def min_opp_dist(x, y):
        if not opp_list:
            return 99
        dmin = 99
        for ox, oy in opp_list:
            d = abs(ox - x) + abs(oy - y)
            if d < dmin: dmin = d
        return dmin

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if (nx, ny) in opp_t:
            v = 120
        elif (nx, ny) in unclaimed:
            v = 35
        elif (nx, ny) in self_t:
            v = 10
        else:
            v = 6

        v += 2.2 * edge_dist(nx, ny)  # prefer interior to counter edge-claim
        v += -1.6 * (abs(nx - cx) + abs(ny - cy) )  # stay near center
        v += 2.0 * min_opp_dist(nx, ny)  # don't over-commit onto opponent frontier unless capturing
        # small tie-break toward keeping progress north/east (deterministic)
        v += 0.01 * (nx * 0.37 + ny * 0.63)

        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]