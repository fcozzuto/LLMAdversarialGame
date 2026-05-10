def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy = int(sx), int(sy)
    except:
        sx, sy = 0, 0
    try:
        ox, oy = int(ox), int(oy)
    except:
        ox, oy = 0, 0

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unclaimed.add((int(p[0]), int(p[1])))

    self_count = observation.get("self_territory_count", None)
    opp_count = observation.get("opponent_territory_count", None)
    if self_count is None:
        self_terr = set()
        for p in (observation.get("self_territory", []) or []):
            if isinstance(p, (list, tuple)) and len(p) == 2:
                self_terr.add((int(p[0]), int(p[1])))
        self_count = len(self_terr)
    if opp_count is None:
        opp_terr = set()
        for p in (observation.get("opponent_territory", []) or []):
            if isinstance(p, (list, tuple)) and len(p) == 2:
                opp_terr.add((int(p[0]), int(p[1])))
        opp_count = len(opp_terr)

    behind = 1 if opp_count > self_count else 0
    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if unclaimed:
        target = min(unclaimed, key=lambda p: (md((sx, sy), p), p[0], p[1]))
    else:
        target = (ox, oy)

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            sc = -10**12
        else:
            if unclaimed:
                sc = -md((nx, ny), target)
            else:
                sc = md((nx, ny), (ox, oy)) if behind else -md((nx, ny), (ox, oy))
        if sc > best_sc:
            best_sc, best = sc, [dx, dy]
    if best is None:
        return [0, 0]
    return best