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
        unclaimed = set(resources)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose a frontier target: unclaimed adjacent to opponent territory; else closest opponent territory.
    opp_neighbors = set()
    for (x, y) in oppT:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if clamp_in(nx, ny) and (nx, ny) not in oppT:
                    opp_neighbors.add((nx, ny))
    candidates = []
    if unclaimed:
        for c in opp_neighbors:
            if c in unclaimed:
                candidates.append(c)
    if not candidates and oppT:
        candidates = list(oppT)
    if not candidates:
        # fallback: go to nearest unclaimed or toward opponent
        candidates = list(unclaimed) if unclaimed else [(ox, oy)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Deterministic target ordering: prefer closeness to self, then progress toward opponent.
    candidates.sort(key=lambda p: (md((sx, sy), p), -md((ox, oy), p), p[0], p[1]))
    tx, ty = candidates[0]

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not clamp_in(nx, ny):
            nx, ny = sx, sy  # engine would reject; we mirror by staying put
        enter_opp = (nx, ny) in oppT
        enter_self = (nx, ny) in selfT
        # Evaluate: capture pressure, reduce distance to target, avoid drifting away from frontier.
        score = 0
        score += 1000 if enter_opp else 0
        score += 50 if (nx, ny) in unclaimed else 0
        score += 10 if not enter_self else 0
        score -= 3 * (md((nx, ny), (tx, ty)))
        # additional tie-break: progress toward opponent corner
        score += 2 * (md((sx, sy), (ox, oy)) - md((nx, ny), (ox, oy)))
        key = (-score, dx, dy)  # higher score preferred; deterministic tie via dx/dy
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]