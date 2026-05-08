def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe_step(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return x, y
        return nx, ny

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_value(x, y):
        # Counter edge-claim: punish being too close to opponent while stealing/advancing into contested cells.
        v = 0.0
        if (x, y) in oppT:
            v += 120.0
        if (x, y) in unclaimed:
            v += 18.0
        if (x, y) in selfT:
            v += 3.0
        # Prefer moving away slightly from opponent (avoid getting corralled on edges), but still attack when possible.
        v -= 1.2 * dist(x, y, ox, oy)
        cx, cy = center
        v -= 0.03 * (abs(x - cx) + abs(y - cy))
        return v

    best = None
    bestv = -1e18
    for dx1, dy1 in dirs:
        x1, y1 = safe_step(sx, sy, dx1, dy1)
        v1 = cell_value(x1, y1)
        # 2-step deterministic lookahead to avoid short-term edge traps.
        best2 = v1
        for dx2, dy2 in dirs:
            x2, y2 = safe_step(x1, y1, dx2, dy2)
            v2 = v1 * 0.35 + cell_value(x2, y2) * 0.65
            if v2 > best2:
                best2 = v2
        # Tie-break by fixed dir order preference.
        if best is None or best2 > bestv:
            bestv = best2
            best = (dx1, dy1)

    return [int(best[0]), int(best[1])]