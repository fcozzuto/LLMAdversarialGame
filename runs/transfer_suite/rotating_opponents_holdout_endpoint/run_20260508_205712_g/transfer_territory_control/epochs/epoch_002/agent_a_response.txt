def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []
    self_territory = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opponent_territory = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    self_count = observation.get("self_territory_count", 0)
    opp_count = observation.get("opponent_territory_count", 0)

    obs = set(tuple(p) for p in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not unclaimed:
        # fallback: pressure opponent territory or drift toward center
        tx, ty = ox, oy
        if self_count >= opp_count:
            tx, ty = w // 2, h // 2
    else:
        if self_count >= opp_count:
            tx, ty = min(unclaimed, key=lambda p: (dist((sx, sy), p), p[0], p[1]))
        else:
            tx, ty = min(unclaimed, key=lambda p: (-dist((sx, sy), p), dist((ox, oy), p), p[0], p[1]))

    center = (w // 2, h // 2)
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        n = (nx, ny)
        score = 0.0
        if n in opponent_territory:
            score += 2.5
        elif n not in self_territory:
            # unclaimed cells only (since obstacles already filtered)
            score += 1.2 if n in map(tuple, unclaimed) else 0.0
        score += 0.15 * (dist(n, (ox, oy)) - dist(n, (sx, sy)))  # keep pressure while not suiciding
        score += -0.30 * dist(n, (tx, ty))  # move toward current target
        score += -0.05 * dist(n, center)    # mild center bias
        # deterministic tie-breaker
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]