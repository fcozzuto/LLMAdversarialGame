def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def rep(p):
        if isinstance(p, dict):
            q = p.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
            return None
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return (p[0], p[1])
        return None

    rpos = []
    for r in resources:
        q = rep(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if not rpos:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in candidates:
            v = -md((nx, ny), (tx, ty)) + 0.15 * (md((nx, ny), (ox, oy)) - md((sx, sy), (ox, oy)))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Deny/resource-control heuristic:
    # Prefer resources closer to self, but discourage letting opponent have a closer claim.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in candidates:
        my_best = 10**9
        op_best = 10**9
        nearest = None
        for r in rpos:
            d1 = md((nx, ny), r)
            d2 = md((ox, oy), r)
            if d1 < my_best:
                my_best = d1
                nearest = r
            if d2 < op_best:
                op_best = d2
        # Target control: if we can become closer than opponent to the nearest resource, boost strongly.
        control = (op_best - my_best)
        # Softly spread away from opponent to reduce direct contest collisions.
        away = md((nx, ny), (ox, oy)) - md((sx, sy), (ox, oy))
        # Small tie-break: prefer moving closer to the single best target resource.
        tie = -my_best
        # If staying captures a nearby resource, reward it.
        stay_bonus = 0.6 if (dx == 0 and dy == 0 and nearest is not None and my_best == 0) else 0.0
        val = 2.2 * control + 0.35 * away + 0.25 * tie + stay_bonus
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]