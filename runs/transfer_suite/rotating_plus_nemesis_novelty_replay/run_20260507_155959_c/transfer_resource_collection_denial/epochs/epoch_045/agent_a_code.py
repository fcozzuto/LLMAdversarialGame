def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if (sx, sy) in obs:
        return [0, 0]

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        mypos = (nx, ny)
        val = None
        for rx, ry in res:
            dself = dist(mypos, (rx, ry))
            dopp = dist((ox, oy), (rx, ry))
            # Prefer resources we can reach strictly before opponent; else minimize lead deficit.
            lead = dopp - dself
            if lead >= 1:
                key = (0, -lead, dself, rx, ry)   # earlier arrival first, then closer
            else:
                key = (1, lead, dself, rx, ry)    # avoid losing races; then closest
            if val is None or key < val:
                val = key
        # Choose move that maximizes winning-ness (minimizes val key lexicographically as constructed).
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]