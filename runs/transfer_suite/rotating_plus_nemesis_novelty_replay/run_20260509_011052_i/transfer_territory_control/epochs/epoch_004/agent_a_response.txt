def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    opp_count = observation.get("opponent_territory_count", len(opp_terr))
    self_count = observation.get("self_territory_count", len(self_terr))
    aggressive = 1 if opp_count > self_count else 0

    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in opp_terr:
            score += 10.0 if aggressive else 8.0
        elif (nx, ny) in unclaimed:
            score += 5.0 if aggressive else 4.0
        elif (nx, ny) in self_terr:
            score += 1.0
        else:
            score += 0.5

        adj_opp = 0
        for ddx, ddy in neighbors:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in opp_terr:
                adj_opp += 1
        if adj_opp:
            score += (2.0 + 0.6 * adj_opp) if aggressive else (1.5 + 0.4 * adj_opp)

        dist_center = abs(nx - cx) + abs(ny - cy)
        score += -0.08 * dist_center

        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        score += (0.05 * dist_to_opp) if not aggressive else (-0.04 * dist_to_opp)

        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]