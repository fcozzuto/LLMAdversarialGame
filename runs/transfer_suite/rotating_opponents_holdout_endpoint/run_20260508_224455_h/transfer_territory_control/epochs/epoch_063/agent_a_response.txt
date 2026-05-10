def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(obj):
        s = set()
        for c in obj or []:
            if not isinstance(c, (list, tuple)) or len(c) < 2:
                continue
            x, y = c[0], c[1]
            s.add((int(x), int(y)))
        return s

    un = to_set(observation.get("unclaimed_cells"))
    myt = to_set(observation.get("self_territory"))
    opt = to_set(observation.get("opponent_territory"))
    obst = to_set(observation.get("obstacles"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    adj4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def unclaimed_adj_count(x, y):
        c = 0
        for dx, dy in adj4:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in un:
                c += 1
        return c

    def score_cell(x, y):
        if (x, y) in obst:
            return -10**9
        dmo = abs(x - ox) + abs(y - oy)
        if (x, y) in opt:
            base = 14
        elif (x, y) in un:
            base = 8
        elif (x, y) in myt:
            base = 2
        else:
            base = 1
        frontier = unclaimed_adj_count(x, y)
        near_opp = 1 if dmo == 1 else 0
        return base + 1.5 * frontier + 0.6 * near_opp - 0.08 * dmo

    best = None
    best_sc = None
    best_tie = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            if not inside(sx, sy) or (sx, sy) in obst:
                nx, ny = sx, sy
            else:
                nx, ny = sx, sy
                dx, dy = 0, 0
        sc = score_cell(nx, ny)
        tie = (abs(nx - ox) + abs(ny - oy), -unclaimed_adj_count(nx, ny), dx == 0 and dy == 0)
        if best_sc is None or sc > best_sc or (sc == best_sc and tie < best_tie):
            best_sc = sc
            best_tie = tie
            best = [dx, dy]
    return [int(best[0]), int(best[1])]