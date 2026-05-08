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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    opp_list = list(opp_t)
    def min_opp_dist(x, y):
        if not opp_list:
            return 99
        dmin = 99
        for ox, oy in opp_list:
            d = abs(ox - x) + abs(oy - y)
            if d < dmin:
                dmin = d
        return dmin

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    bestv = -10**18

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0.0
        if (nx, ny) in opp_t:
            v += 60.0
        elif (nx, ny) in unclaimed:
            v += 12.0 + edge_dist(nx, ny) * 1.5
        elif (nx, ny) in self_t:
            v += 3.0 + edge_dist(nx, ny) * 0.2
        else:
            v += 1.0

        v += min_opp_dist(nx, ny) * 0.35

        dc = abs(nx - cx) + abs(ny - cy)
        v += (w + h - dc) * 0.05

        if v > bestv or (v == bestv and (dx, dy) < (best_move[0], best_move[1])):
            bestv = v
            best_move = [dx, dy]

    return best_move