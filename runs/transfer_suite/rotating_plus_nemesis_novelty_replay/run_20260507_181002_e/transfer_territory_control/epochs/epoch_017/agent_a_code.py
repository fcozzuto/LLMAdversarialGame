def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))

    if not unclaimed:
        unclaimed = set(resources)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    # Precompute nearest targets from current position (cheap).
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    nearest_opp = None
    if oppT:
        nearest_opp = min(oppT, key=lambda t: man((sx, sy), t))
    nearest_uncl = None
    if unclaimed:
        nearest_uncl = min(unclaimed, key=lambda t: man((sx, sy), t))

    oxp, oyp = int(op[0]), int(op[1])
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        cell = (nx, ny)
        val = 0
        # Big reward for flipping opponent territory.
        if cell in oppT:
            val += 1000
        # Medium reward for claiming unclaimed.
        if cell in unclaimed:
            val += 200
        # Small incentive to keep/extend own territory.
        if cell in selfT:
            val += 30
        # Avoid getting stuck: prefer moving closer to the nearest interesting cell.
        if nearest_opp is not None:
            val += 40 - 2 * man((nx, ny), nearest_opp)
        if nearest_uncl is not None:
            val += 20 - 1 * man((nx, ny), nearest_uncl)
        # Keep general pressure toward the center and slightly away from opponent position.
        val += 0.5 * (-(abs(nx - cx) + abs(ny - cy)))
        val += 0.2 * (-(abs(nx - oxp) + abs(ny - oyp)))

        # Tie-break deterministically by dir order, then by higher value, then lexicographic move.
        key = (val, -abs(dx) - abs(dy), dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]