def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        if (x, y) in obstacles or not inb(x, y):
            return -10**9
        val = 0
        if (x, y) in unclaimed:
            val += 3
        if (x, y) in opp_terr:
            val += 4
        if (x, y) in self_terr:
            val += 1
        if unclaimed:
            t = min(unclaimed, key=lambda c: abs(c[0] - x) + abs(c[1] - y))
            val += -0.15 * (abs(t[0] - x) + abs(t[1] - y))
        if opp_terr:
            t2 = min(opp_terr, key=lambda c: abs(c[0] - x) + abs(c[1] - y))
            val += -0.08 * (abs(t2[0] - x) + abs(t2[1] - y))
        return val

    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score_cell(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < best):
            best_val = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]