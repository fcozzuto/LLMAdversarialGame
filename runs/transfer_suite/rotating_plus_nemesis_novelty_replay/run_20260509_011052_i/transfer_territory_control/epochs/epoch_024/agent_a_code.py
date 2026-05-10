def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def score_cell(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return -10**9
        if (x, y) in self_terr:
            base = 0.0
        elif (x, y) in opp_terr:
            base = 8.0
        elif (x, y) in unclaimed:
            base = 3.5
        else:
            base = 1.0  # other territory region (rare)
        adj_opp = 0
        adj_unclaimed = 0
        adj_self = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_terr:
                adj_opp += 1
            if (nx, ny) in unclaimed:
                adj_unclaimed += 1
            if (nx, ny) in self_terr:
                adj_self += 1
        dist_opp = abs(ox - x) + abs(oy - y)
        dist_term = -0.12 * dist_opp
        # Prefer expanding toward unknown while staying close enough to contest opponent boundary.
        return base + 1.2 * adj_unclaimed + 1.0 * adj_opp - 0.6 * adj_self + dist_term

    best = None
    best_s = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        s = score_cell(nx, ny)
        if s > best_s or (s == best_s and (dx, dy) < tuple(best or (2, 2))):
            best_s = s
            best = (dx, dy)
    return [int(best[0]), int(best[1])]