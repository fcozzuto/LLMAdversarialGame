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
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    if not unclaimed:
        unclaimed = set(resources)  # fallback

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def man(a, b):  # manhattan
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a deterministic "frontier" target: unclaimed if available else opponent territory else center
    if unclaimed:
        target = min(unclaimed, key=lambda p: (man((sx, sy), p), man((ox, oy), p)))
    elif oppT:
        target = min(oppT, key=lambda p: (man((sx, sy), p), man((ox, oy), p)))
    else:
        target = (int(round(cx)), int(round(cy)))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (None, -10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue  # avoid wasting moves hitting obstacle
        p = (nx, ny)

        # Base reward structure emphasizing flips (enter opponent territory) and claiming (unclaimed)
        score = 0
        if p in oppT:
            score += 1200 - 3 * man(p, target)
        if p in unclaimed:
            score += 260 - 2 * man(p, target)
        if p in selfT:
            score += 20 - 1 * man(p, target)

        # Territorial pressure: approach target but discourage drifting away from opponent frontiers
        score += 8 * (w - man(p, target))
        score += 5 * (h - man(p, (ox, oy)))  # keep pressure near opponent
        # Slight preference to reduce distance to target
        score += -3 * man(p, target)

        # Deterministic tie-break: lower dx, then dy, then lexicographic position
        tie = (score, -dx, -dy, nx, ny)
        if tie > (best[1], 0, 0, 0, 0):
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]