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

    def rep(pos):
        if isinstance(pos, (list, tuple)) and len(pos) >= 2:
            return (pos[0], pos[1])
        if isinstance(pos, dict):
            q = pos.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
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
        # deterministic "anti-sweep_rows": drift to center band while staying legal
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in candidates:
            v = (abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy))
            if bestv is None or v < bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a move by scoring how much it improves our "winning" margin to resources.
    # margin = (opp_dist - self_dist), higher means we're closer than opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in candidates:
        best_margin = None
        best_time = None
        best_pos = None
        for r in rpos:
            ds = md((nx, ny), r)
            do = md((ox, oy), r)
            margin = do - ds
            # time-to-resource tie-breaker: prefer closer when margin same
            if best_margin is None or margin > best_margin or (margin == best_margin and (best_time is None or ds < best_time)):
                best_margin, best_time, best_pos = margin, ds, r

        # Additional nudge: penalize moves that increase distance to our chosen target heavily
        # and slightly favor staying closer to target to keep momentum.
        tds = best_time if best_time is not None else 0
        score = (-(best_margin), tds, abs(nx - sx) + abs(ny - sy), nx, ny)
        # We want max margin => minimize -margin; deterministic tie-breakers included.
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]