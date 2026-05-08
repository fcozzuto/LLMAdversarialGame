def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    sp_ox, sp_oy = (observation.get("opponent_position") or (w - 1, h - 1))
    sp_ox, sp_oy = int(sp_ox), int(sp_oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    opp_list = list(opp_t)
    if not opp_list:
        def min_opp_dist(x, y):
            return abs(sp_ox - x) + abs(sp_oy - y)
    else:
        def min_opp_dist(x, y):
            dmin = 10**9
            for ox, oy in opp_list:
                d = abs(ox - x) + abs(oy - y)
                if d < dmin:
                    dmin = d
            return dmin

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles and not (dx == 0 and dy == 0):
            v = -10**12
        else:
            v = 0
            if (nx, ny) in unclaimed:
                v += 6
            if (nx, ny) in opp_t:
                v += 12
            if (nx, ny) in self_t:
                v += 2
            v += 0.25 * min_opp_dist(nx, ny)
            v += 0.05 * edge_dist(nx, ny)
        if v > bestv:
            bestv = v
            best_move = [dx, dy]
    return best_move