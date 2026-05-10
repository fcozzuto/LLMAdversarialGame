def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, px, py):
        return abs(px - x) + abs(py - y)

    def nearest_unclaimed_dist(x, y):
        if unclaimed:
            best = 10**9
            for ux, uy in unclaimed:
                d = dist(x, y, ux, uy)
                if d < best:
                    best = d
            return best
        return 10**6

    def adj_to_self(x, y):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in self_terr:
                c += 1
        return c

    best = (float("-inf"), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            sc = -1e6
        else:
            sc = 0
            if (nx, ny) in opp_terr:
                sc += 7
            elif (nx, ny) in unclaimed:
                sc += 6
            elif (nx, ny) in self_terr:
                sc += 1
            sc += 1.5 * adj_to_self(nx, ny)
            d_opp = dist(nx, ny, ox, oy)
            sc += -0.35 * d_opp
            sc += -0.15 * nearest_unclaimed_dist(nx, ny)
            # If we can immediately step closer to opponent territory, reward it slightly
            if opp_terr:
                dmin = min(dist(nx, ny, px, py) for px, py in opp_terr)
                sc += -0.08 * dmin
            # Penalize being adjacent to many opponent cells (avoid getting swept)
            sc += -0.6 * sum((nx + a, ny + b) in opp_terr for a, b in dirs4)
        if sc > best[0]:
            best = (sc, dx, dy)
    return [int(best[1]), int(best[2])]