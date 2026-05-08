def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_my(x, y):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in self_terr:
                c += 1
        return c

    def adj_opp(x, y):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_terr:
                c += 1
        return c

    def cell_value(x, y):
        if not inb(x, y):
            return -10**9
        if (x, y) in obstacles:
            return -10**9
        d_center = abs(x - cx) + abs(y - cy)
        d_opppos = abs(x - ox) + abs(y - oy)
        v = 0
        if (x, y) in opp_terr:
            v += 12
        elif (x, y) in self_terr:
            v += 2
        elif (x, y) in unclaimed:
            v += 7
        else:
            v += 1
        v += 3 * (adj_my(x, y))
        v += -1.5 * (adj_opp(x, y))
        v += -0.25 * d_center  # go toward center
        v += -0.12 * d_opppos  # also slightly pressure toward opponent
        return v

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = cell_value(nx, ny)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]