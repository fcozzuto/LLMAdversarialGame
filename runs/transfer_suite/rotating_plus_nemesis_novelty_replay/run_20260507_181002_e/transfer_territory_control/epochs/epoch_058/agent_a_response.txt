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
    resources = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    if not unclaimed and resources:
        unclaimed = set(resources)
    if not unclaimed:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    candidates = []
    for tx, ty in unclaimed:
        if (tx, ty) in obstacles or not inb(tx, ty):
            continue
        ds = abs(sx - tx) + abs(sy - ty)
        do = abs(ox - tx) + abs(oy - ty)
        if selfT:
            nds = 10**9
            for px, py in selfT:
                d = abs(px - tx) + abs(py - ty)
                if d < nds: nds = d
        else:
            nds = ds
        if oppT:
            ndo = 10**9
            for px, py in oppT:
                d = abs(px - tx) + abs(py - ty)
                if d < ndo: ndo = d
        else:
            ndo = do
        center = abs(tx - cx) + abs(ty - cy)
        # Prefer targets where we are closer than opponent (territory counterclaim archetype)
        val = (ndo - nds) * 10 - ds + (28 - center) * 0.2
        candidates.append((val, tx, ty))
    if not candidates:
        return [0, 0]

    _, tx, ty = max(candidates, key=lambda t: t[0])

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx, sy + dy
    if not inb(nx, ny) or (nx, ny) in obstacles:
        # Try axis-only fallback deterministically
        for adx, ady in ((dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)):
            px, py = sx + adx, sy + ady
            if inb(px, py) and (px, py) not in obstacles:
                return [int(adx), int(ady)]
        return [0, 0]
    return [int(dx), int(dy)]