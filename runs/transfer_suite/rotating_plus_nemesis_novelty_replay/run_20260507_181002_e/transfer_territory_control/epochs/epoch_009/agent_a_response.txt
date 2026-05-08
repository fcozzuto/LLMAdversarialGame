def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    if not unclaimed:
        unclaimed = set(resources)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    adj8 = dirs

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def has_adj_opp(cell):
        x, y = cell
        for dx, dy in adj8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in oppT:
                return True
        return False

    candidates = []
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        in_self = cell in selfT
        in_opp = cell in oppT
        # Prefer: stealing opp boundary, then claiming unclaimed/resource, while keeping distance from opp.
        if in_opp:
            steal = 80
        else:
            steal = 0
        if cell in unclaimed:
            claim = 40
        elif cell in resources:
            claim = 20
        else:
            claim = 0
        if has_adj_opp(cell):
            boundary = 10 if not in_opp else 15
        else:
            boundary = 0
        # Expansion tendency: prefer moving to cells that are not already ours
        expand = -5 if in_self else 6
        # Avoid walking straight into opponent if we aren't stealing
        d_opp = dist((nx, ny), (ox, oy))
        avoid = 12 * min(d_opp, 6)
        # If we are adjacent to opp territory, slightly prioritize approaching it (deterministic via score).
        approach = 0
        if (nx, ny) not in oppT and has_adj_opp(cell):
            approach = 8
        score = steal + claim + boundary + expand + avoid + approach

        # Tie-break deterministically: prefer larger dx then dy to keep consistent.
        key = (score, dx, dy)
        if key > best:
            best = key
            candidates = [(dx, dy)]

    if candidates:
        return [int(candidates[0][0]), int(candidates[0][1])]
    return [0, 0]