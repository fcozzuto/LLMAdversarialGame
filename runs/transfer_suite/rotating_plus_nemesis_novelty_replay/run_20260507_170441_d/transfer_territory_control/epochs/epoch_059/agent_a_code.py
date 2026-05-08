def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def adj_to(setcells, x, y):
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            if (x + dx, y + dy) in setcells:
                return True
        return False

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        v = 0.0
        if (nx, ny) in opp_t:
            v += 1000.0
            v += 50.0 if adj_to(opp_t, nx, ny) else 0.0
        elif (nx, ny) in unclaimed:
            v += 500.0
            v += 220.0 if adj_to(opp_t, nx, ny) else 0.0
            v += 30.0 if adj_to(self_t, nx, ny) else 0.0
            v += 0.5 * (10 - (abs(nx - ox) + abs(ny - oy)))
            v -= 0.2 * (abs(nx - cx) + abs(ny - cy))
        elif (nx, ny) in self_t:
            v += 12.0
            v += 10.0 if adj_to(unclaimed, nx, ny) else 0.0
            v -= 1.0 if (adj_to(opp_t, nx, ny) and adj_to(unclaimed, nx, ny)) else 0.0
        else:
            v += 1.0

        # small deterministic preference: closer to opponent if equal
        v += -0.01 * (abs(nx - ox) + abs(ny - oy))

        key = (v, dx, dy)
        if best is None or key > (bestv, best[0], best[1]):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]