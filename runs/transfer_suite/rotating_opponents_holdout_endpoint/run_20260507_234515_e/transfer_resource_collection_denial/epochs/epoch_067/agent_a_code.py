def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Also consider "resource priority" by closeness to us and how much closer we are than opponent.
    # If we can likely secure a resource first, prefer it; otherwise move toward the closest still.
    best = None
    best_key = 10**18
    for rx, ry in res:
        dS = man(sx, sy, rx, ry)
        dO = man(ox, oy, rx, ry)
        # Negative means advantage to us; we minimize key -> maximize advantage by subtracting.
        advantage = dO - dS
        # Slightly penalize targets we can't approach directly (adjacent obstacle count).
        adj_block = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (rx + dx, ry + dy) in obs:
                adj_block += 1
        key = (dS * 1.0) - (advantage * 1.25) + adj_block * 0.2
        # Prefer not-too-far targets early to avoid giving sweep-row opponents tempo.
        key += max(0, dS - 5) * 0.15
        if key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy)]
    for ddx, ddy in candidates:
        nx, ny = sx + ddx, sy + ddy
        if inb(nx, ny):
            return [int(ddx), int(ddy)]

    # Fallback: scan local 3x3 for any valid move toward best.
    best_move = [0, 0]
    best_local = 10**18
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny):
                dist = man(nx, ny, rx, ry)
                # Prefer reducing distance.
                if dist < best_local:
                    best_local = dist
                    best_move = [int(ddx), int(ddy)]
    return best_move