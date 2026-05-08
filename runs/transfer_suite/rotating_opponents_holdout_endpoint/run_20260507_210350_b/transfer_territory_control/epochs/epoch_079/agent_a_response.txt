def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    moves.sort()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(x, y):
        if (x, y) in obstacles:
            return -10**6
        if (x, y) in opp_terr:
            return 6.0
        if (x, y) in self_terr:
            return 1.5
        if (x, y) in unclaimed:
            return 3.5
        return 0.5

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp_now = abs(sx - ox) + abs(sy - oy)
        d_opp_new = abs(nx - ox) + abs(ny - oy)
        d_ctr_now = abs(sx - cx) + abs(sy - cy)
        d_ctr_new = abs(nx - cx) + abs(ny - cy)

        val = 0.0
        val += cell_score(nx, ny)
        val += 1.2 * (d_opp_now - d_opp_new)  # move closer to opponent
        val += 0.6 * (d_ctr_now - d_ctr_new)  # prefer center
        val += 0.3 * (-abs((nx - ox) - (ny - oy)))  # mild diagonal pressure
        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]