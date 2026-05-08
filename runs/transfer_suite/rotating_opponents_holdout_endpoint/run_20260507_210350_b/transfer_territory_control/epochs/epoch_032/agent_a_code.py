def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    def to_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            try:
                s.add((int(p[0]), int(p[1])))
            except Exception:
                pass
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    resources = to_set(observation.get("resources"))
    self_terr = to_set(observation.get("self_territory"))
    opp_terr = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def min_dist_to_set(x, y, s):
        if not s:
            return 999
        best = 999
        for tx, ty in s:
            d = md(x, y, tx, ty)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    candidates = []
    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    best_move = candidates[0]
    best_score = -10**18
    for dx, dy, nx, ny in candidates:
        # Prefer secure expansion toward center, avoid being adjacent to opponent,
        # but heavily reward flipping into opponent territory when possible.
        dist_center = abs(nx - cx) + abs(ny - cy)
        opp_close = min_dist_to_set(nx, ny, opp_terr)
        in_opp = (nx, ny) in opp_terr
        in_un = (nx, ny) in unclaimed
        in_res = (nx, ny) in resources

        score = 0
        score += 2.2 * (-dist_center)
        score += 1.4 * (opp_close)  # stay away from opponent to prevent edge locking
        if in_opp:
            score += 25  # flipping opponent control on entry is valuable
        if in_un:
            score += 6
        if in_res:
            score += 4
        if (nx, ny) in self_terr:
            score += 1  # maintain territorial presence
        # Extra deterministic tie-breaker: favor lexicographically smaller move
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]