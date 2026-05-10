def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        s = 0
        if (nx, ny) in oppT:
            s += 120
        elif (nx, ny) in unclaimed:
            s += 55
        elif (nx, ny) in selfT:
            s += 15
        else:
            s += 25

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_prev = abs(sx - cx) + abs(sy - cy)
        s += (dist_prev - dist_center) * 3

        dist_opp = abs(nx - ox) + abs(ny - oy)
        s += max(0, 10 - dist_opp) * 2

        if nx == sx and ny == sy:
            s -= 6

        # Local obstacle/escape shaping: prefer moves with more free neighbors
        free = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    free += 1
        s += free * 1
        return s

    best = None
    best_s = -10**18
    for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny)
        if best is None or sc > best_s:
            best_s = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]