def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    selfT = to_set("self_territory")
    oppT = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    order = {m: i for i, m in enumerate(moves)}

    # Build frontier targets near our territory first.
    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    frontier = set()
    for x, y in selfT:
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                frontier.add((nx, ny))
    candidates = sorted(frontier) if frontier else sorted(unclaimed) if unclaimed else []

    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a deterministic target among candidates using opponent pressure.
    target = None
    if candidates:
        bestk = None
        for t in candidates:
            tx, ty = t
            k = (man(w // 2, h // 2, tx, ty), man(sx, sy, tx, ty), -man(tx, ty, ox, oy), tx, ty)
            if bestk is None or k < bestk:
                bestk = k
                target = t
    else:
        target = (w // 2, h // 2)

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        val = 0.0
        if (nx, ny) in unclaimed:
            val += 6.0
        if (nx, ny) in oppT:
            val += 2.5  # flipping on entry; exact scoring handled by env, but encourage access.
        if (nx, ny) in selfT:
            val += 0.5

        # Progress to target and avoid getting too close to opponent territory for safety.
        val += -0.7 * man(nx, ny, tx, ty)
        if oppT:
            mind = min(manh(nx, ny, ex, ey) for (ex, ey) in oppT)
            val += 0.25 * mind  # prefer moves that keep some distance from opponent held cells.

        # If opponent is very close, bias capturing unclaimed near us.
        if man(sx, sy, ox, oy) <= 2 and (nx, ny) in unclaimed:
            val += 1.5

        # Deterministic tie-break.
        key = (val, -order[(dx, dy)])
        if key > (best_val, -order[best_move]):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]