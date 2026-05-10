def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = int(observation.get("turns_remaining", 0))

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # If no visible resources, drift toward center unless blocked
    if not resources:
        dirs0 = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs0:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            sc = dist(nx, ny, cx, cy)
            if sc < best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Choose target by race heuristic: prefer resources we can reach sooner than opponent.
    best_t = None
    best_val = 10**18
    opp_weight = 1.15
    time_weight = 0.0 if turns_remaining > 0 else 0.0
    for rx, ry in res:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Penalize resources opponent can reach much earlier.
        val = ds - opp_weight * do + time_weight * ds
        # Mild preference for being closer when still tied
        val += 0.02 * ds
        if val < best_val:
            best_val = val
            best_t = (rx, ry)

    rx, ry = best_t

    # Greedy step: minimize (self distance + slight lead over opponent) to the chosen target
    best = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        dsn = dist(nx, ny, rx, ry)
        don = dist(ox, oy, rx, ry)
        # Encourage capturing quickly, discourage letting opponent get relative advantage
        sc = dsn + 0.35 * max(0, don - dsn)
        # If denier tries to block, keep some preference for moving toward target even when close
        if dsn == 0:
            sc -= 0.5
        if sc < best[0]:
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]