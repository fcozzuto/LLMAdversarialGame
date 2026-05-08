def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    selfT = set(tuple(t) for t in (observation.get("self_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))
    oppT = set(tuple(t) for t in (observation.get("opponent_territory") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh4(x, y):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                yield nx, ny

    # pick a target: unclaimed adjacent to our territory, else any unclaimed, else a step toward center
    frontier = []
    for (x, y) in selfT:
        for nx, ny in neigh4(x, y):
            if (nx, ny) in unclaimed and (nx, ny) not in blocked:
                frontier.append((nx, ny))
    if frontier:
        targets = frontier
    else:
        targets = [c for c in unclaimed if c not in blocked]
    if not targets:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx, ty = int(round(cx)), int(round(cy))
        targets = [(tx, ty)]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # choose best immediate move with deterministic scoring
    best = None
    best_s = -10**18
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue
        candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    # primary: maximize claiming value; secondary: minimize distance to best target; tertiary: avoid opponent
    # (small deterministic tie-break by move order)
    t = min(targets, key=lambda c: (manh(c, (sx, sy)), c[0], c[1]))
    for nx, ny, dx, dy in candidates:
        s = 0
        if (nx, ny) in unclaimed:
            s += 10000
        if (nx, ny) in selfT:
            s += 50
        if (nx, ny) in oppT:
            s += 1800  # flipping on entry
        # prefer staying away from opponent unless flipping value exists
        s -= 3 * manh((nx, ny), (ox, oy))
        # prefer progress toward our chosen target
        s -= 2 * manh((nx, ny), t)
        # slight preference to move off current cell if stuck
        if (nx, ny) == (sx, sy):
            s -= 10
        if s > best_s:
            best_s = s
            best = (dx, dy)
    return [int(best[0]), int(best[1])]