def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x0, y0 = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))
    resources = set(map(tuple, observation.get("resources", [])))
    opp = observation.get("opponent_position", (None, None))
    ox, oy = opp if isinstance(opp, (list, tuple)) and len(opp) == 2 else (None, None)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def dist(a, b): 
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return abs(dx) + abs(dy)

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def score(x, y):
        if not free(x, y): 
            return -10**9
        dcen = abs(x - cx) + abs(y - cy)
        s = 0
        if (x, y) in resources: s += 1200
        if (x, y) in unclaimed: s += 400 + 3 * min(x, w - 1 - x, y, h - 1 - y) - 2 * dcen
        if (x, y) in opp_terr: s -= 120 + 2 * dist((x, y), (ox, oy)) if ox is not None else -120
        if (x, y) in self_terr: s += 20 - 0.5 * dcen
        if ox is not None:
            s += 15 * (dist((x, y), (ox, oy)) == 0) - 2 * dist((x, y), (ox, oy))
        return int(s)

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = x0 + dx, y0 + dy
        sc = score(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    dx, dy = best if best is not None else (0, 0)
    return [int(dx), int(dy)]