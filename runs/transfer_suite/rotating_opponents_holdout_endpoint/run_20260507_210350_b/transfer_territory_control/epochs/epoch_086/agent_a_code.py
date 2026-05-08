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
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def frontier_score(x, y):
        c = 0
        for ax, ay in dirs:
            nx, ny = x + ax, y + ay
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def cell_base(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in self_terr:
            return 1.5
        if (x, y) in unclaimed:
            return 8.0
        if (x, y) in opp_terr:
            return 6.0
        return 3.0

    best = (float("-inf"), 0, 0)
    # Tie-break deterministically by preferring non-stay, then dx, then dy
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        b = cell_base(nx, ny)
        if b <= -10**8:
            continue
        distc = abs(nx - cx) + abs(ny - cy)
        toward = (14 - distc) * 0.12
        fr = frontier_score(nx, ny) * 0.9
        # Mild preference to approach opponent territory for potential flipping
        adj_opp = 0
        for ax, ay in dirs:
            ex, ey = nx + ax, ny + ay
            if inb(ex, ey) and (ex, ey) in opp_terr:
                adj_opp = 1
                break
        opp_bonus = 1.2 if adj_opp else 0.0
        val = b + toward + fr + opp_bonus
        stay_pen = 0.2 if (dx == 0 and dy == 0) else 0.0
        val -= stay_pen
        # Deterministic tie-break: higher val, then prefer moves over staying, then lexicographic dx/dy
        move_pref = 1 if not (dx == 0 and dy == 0) else 0
        key = (val, move_pref, -dx, -dy)
        if key > (best[0], best[1], -best[1], -best[2]):
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]