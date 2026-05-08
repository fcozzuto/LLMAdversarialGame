def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def adj_opp(x, y):
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_terr:
                return True
        return False

    # Prefer invading opponent territory, else secure unclaimed near opponent
    best = None
    best_score = -10**18
    candidates = list(unclaimed) + list(opp_terr)
    if not candidates:
        return [0, 0]

    for (x, y) in candidates:
        if not ok(x, y) or (x, y) in self_terr:
            continue
        d = abs(x - sx) + abs(y - sy)
        score = (50 if (x, y) in opp_terr else 0) + (10 if (x, y) in unclaimed else 0)
        if adj_opp(x, y):
            score += 8
        # slight preference to get closer, tie-break deterministically by coordinates
        score -= d
        score += -0.001 * (x + 10 * y)
        if score > best_score:
            best_score = score
            best = (x, y)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Ensure chosen step is not into an obstacle/bounds; if it is, try neighboring deltas deterministically
    for mx, my in [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy)]:
        nx, ny = sx + mx, sy + my
        if ok(nx, ny):
            return [mx, my]

    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if ok(nx, ny):
            return [mx, my]
    return [0, 0]