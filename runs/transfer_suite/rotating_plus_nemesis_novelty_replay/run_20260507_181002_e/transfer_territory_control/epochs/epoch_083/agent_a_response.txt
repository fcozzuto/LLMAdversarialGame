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
    candidates = list(unclaimed) if unclaimed else list(oppT)
    if not candidates:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def edge_pref(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    # Prefer nearest frontier, avoid cells too close to opponent if possible
    candidates.sort(key=lambda t: (
        man(sx, sy, t[0], t[1]),
        man(ox, oy, t[0], t[1]) if t in unclaimed else -man(ox, oy, t[0], t[1]),
        edge_pref(t[0], t[1]),
        t[0], t[1]
    ))
    tx, ty = candidates[0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Heuristic: move toward target, and prefer expanding into unclaimed; don't step into opponent if it doesn't progress
        toward = -man(nx, ny, tx, ty)
        gain = 0
        if (nx, ny) in unclaimed:
            gain += 5
        if (nx, ny) in oppT:
            # flipping is good only if it also moves closer to target
            gain += 2 if man(nx, ny, tx, ty) <= man(sx, sy, tx, ty) else -1
        if (nx, ny) in selfT:
            gain += 1
        # Avoid getting adjacent to opponent while not advancing
        adj_opp = max(abs(nx - ox), abs(ny - oy))
        threat_pen = -2 if adj_opp <= 1 and man(nx, ny, tx, ty) >= man(sx, sy, tx, ty) else 0

        val = toward + gain + threat_pen
        key = (-val, abs(dx), abs(dy), dx, dy)  # deterministic tie-break
        if key < best:
            best = key

    return [best[3], best[4]]