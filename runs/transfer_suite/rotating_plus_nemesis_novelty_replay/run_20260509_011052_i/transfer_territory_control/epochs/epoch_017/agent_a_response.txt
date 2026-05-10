def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    opp_count = int(observation.get("opponent_territory_count", len(opp_terr)))
    self_count = int(observation.get("self_territory_count", len(self_terr)))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_free(nx, ny):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            x2, y2 = nx + dx, ny + dy
            if not inb(x2, y2) or (x2, y2) in obstacles:
                continue
            if (x2, y2) not in self_terr:
                c += 1
        return c

    def dist_center(x, y):
        dx, dy = x - cx, y - cy
        return dx * dx + dy * dy

    aggressive = 1 if opp_count >= self_count else 0
    best = None
    best_val = None
    order = list(range(9))

    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in opp_terr:
            val += 120.0 if aggressive else 90.0
            val += 8.0
            val -= dist_center(nx, ny) * 0.02
        elif (nx, ny) in unclaimed:
            val += 55.0
            val -= dist_center(nx, ny) * 0.03
            val += neigh_free(nx, ny) * 1.2
        elif (nx, ny) in self_terr:
            val -= 8.0
            val += neigh_free(nx, ny) * 0.3
        else:
            val += 5.0
            val -= dist_center(nx, ny) * 0.02
            val += neigh_free(nx, ny) * 0.4

        # Prefer moves that reduce distance to opponent territory centroid (roughly)
        if opp_terr:
            # deterministic approximate centroid: pick lowest dist point among opp_terr
            best_opp = None
            bd = None
            for (px, py) in opp_terr:
                d = (px - cx) * (px - cx) + (py - cy) * (py - cy)
                if bd is None or d < bd:
                    bd = d
                    best_opp = (px, py)
            px, py = best_opp
            val -= ((nx - px) * (nx - px) + (ny - py) * (ny - py)) * (0.015 if aggressive else 0.008)

        if best_val is None or val > best_val or (val == best_val and i < order[order.index(i) if i in order else i]):
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]